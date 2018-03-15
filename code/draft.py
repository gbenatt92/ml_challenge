from dask import dataframe as dd
from data_tools import xz_ndjson_to_parquet
import pandas as pd
from scipy.sparse import coo_matrix
import implicit


def explode_transactions(transactions):
    raw2 = pd.concat([pd.Series(row['user_id'], row['items'].split('|'))
                      for _, row in transactions.iterrows()]).reset_index()
    raw2.columns = ['product_id', 'user_id']
    return dd.from_pandas(raw2, npartitions=4)

def creating_user_product_score(dask_frame):
    dask_frame

if __name__ == "__main__":

    transactions = dd.read_parquet('/app/data/output1/transactions.parquet')
    views = dd.read_parquet('/app/data/output1/views.parquet')

    views = views[['browser_id', 'user_id', 'product_id']]
    raw1 = views[['user_id', 'product_id']]

    raw2 = explode_transactions(transactions)

    raw2['score'] = 10
    raw1['score'] = 1

    total = dd.concat([raw1, raw2], axis=0)

    products = total['product_id'].unique()

    total['user_id'] = total['user_id'].astype('category')
    total['user_id'] = total['user_id'].cat.as_known()

    total['product_id'] = total['product_id'].astype('category')
    total['product_id'] = total['product_id'].cat.as_known()

    scored_data = total.groupby(['product_id', 'user_id'])[
        'score'].sum().reset_index()
    
    users = scored_data['user_id'].unique()
    users = users.sample(0.2,random_state=1234)

    users = users.compute().tolist()
    test_data = scored_data.loc[(scored_data['user_id'].isin(users)),::]

    scored_data = scored_data.loc[~(scored_data['user_id'].isin(users)),::]
    scored_data = scored_data.compute()
    items = coo_matrix((scored_data['score'].astype(float),
                        (scored_data['product_id'].cat.codes,
                         scored_data['user_id'].cat.codes)))
    items = implicit.nearest_neighbours.bm25_weight(items, K1=100, B=0.8)
    items = items.tocsr()
    
    model = implicit.als.AlternatingLeastSquares(factors=20)
    model.fit(items)

    test_users = test_data['user_id'].unique().compute().tolist()
    test =  test_data.compute()
    test =  coo_matrix((test['score'].astype(float),
                            (test['product_id'].cat.codes,
                            test['user_id'].cat.codes)))
    test = implicit.nearest_neighbours.bm25_weight(test, K1=100, B=0.8)
    to_score = test.T.tocsr()
    for userid, username in enumerate(test_data.compute()['user_id'].cat.categories):
        print(model.recommend(userid, to_score, N=10))

    print(model)