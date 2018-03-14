from dask import dataframe as dd
from data_tools import xz_ndjson_to_parquet
import pandas as pd
from scipy.sparse import coo_matrix
import implicit


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flip a switch by setting a flag")
    parser.add_argument('-d', action='store_true')
    
    args = parser.parse_args()

    if args.d:
        xz_ndjson_to_parquet("/app/data/pdpviews.ndjson.xz", '/app/data/intermediate/views.parquet')
        xz_ndjson_to_parquet("/app/data/transactions.ndjson.xz",
                            '/app/data/intermediate/transactions.parquet', items=True)

