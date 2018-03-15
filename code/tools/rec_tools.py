from pyspark.sql import SparkSession
from pyspark.sql.functions import array, col, lit, struct, udf, when
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.sql.types import StringType

def rec_sys(evaluation=False):
    """Runs and saves a series of data processing task to a bunch of parquet
    files.
    """
    spark = SparkSession.builder.appName(
        name="data-ingestion"
    ).config(
        "spark.executor.memory", "1500M"
    ).config("spark.driver.memory", "4G").getOrCreate()

    n = 10

    user_item = spark.read.parquet("/data_proj/intermediate/user_item.parquet").repartition(13000)
    print(user_item.count())
    user_item = user_item.filter(col("score") > 9)  
    print(user_item.count())
    user_model, product_model, user_item = indexer(user_item)

    if evaluation:
        train_evaluate(user_item)

    print("starting ALS")
    als_model = model_fit(user_item)

    print("saving ALS")
    als_model.save("/data_proj/output/als-recsys")

    print("generating recommendations")
    user_recs = als_model.recommendForAllUsers(n)
    user_recs = generate_recommendation(user_recs, user_model, product_model, n)

    browser_user = spark.read.parquet("/data_proj/intermediate/user_browser_ids.parquet").repartition(13000)

    user_recs = user_recs.join(browser_user, user_recs.user_id == browser_user.user_id).drop('user_id')

    print("saving    recommendations")
    user_recs.write.json("/data_proj/output/recommendations")



def indexer(user_item):
    user_item, user_model = indexer_fit_transform(user_item,"user_id")
    user_item, product_model= indexer_fit_transform(user_item,"product_id")
    return user_model, product_model, user_item
    

def indexer_fit_transform(user_item,col_name):
    indexed_col = col_name+'_ind'
    stringIndexer = StringIndexer(inputCol=col_name, outputCol=indexed_col)
    model = stringIndexer.fit(user_item)
    user_item = model.transform(user_item)
    user_item = user_item.drop(col_name)
    return user_item, model


def train_evaluate(user_item):
    (training, test) = user_item.randomSplit([0.8, 0.2])
    model = model_fit(training)
    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="score",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print(rmse)


def model_fit(user_item):
    als = ALS(maxIter=5, regParam=0.01, userCol="user_id_ind", itemCol="product_id_ind", ratingCol="score",
          coldStartStrategy="drop",implicitPrefs=True)
    return als.fit(user_item.repartition(20000))


def generate_recommendation(user_recs, user_model, product_model,n):
    user_id_to_label = IndexToString(
        inputCol="user_id_ind", outputCol="user_id", labels=user_model.labels)
    user_recs = user_id_to_label.transform(user_recs).drop('user_id_ind')

    product_labels_ = array(*[lit(x) for x in product_model.labels])
    recommendations = array(*[when( col("recommendations")[i]["rating"] > 0,
        product_labels_[col("recommendations")[i]["product_id_ind"]].alias("product_id")
    )for i in range(n)])

    return user_recs.withColumn("items", recommendations).drop("recommendations")

    

