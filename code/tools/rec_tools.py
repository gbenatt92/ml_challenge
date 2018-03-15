from pyspark.sql import SparkSession
from pyspark.sql.functions import array, col, lit, when
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.ml.feature import StringIndexer, IndexToString


def rec_sys(evaluation=False):
    """Runs and saves the ALS recommender system and generates recommendations
    for all browser_ids that have made a purchase or visited an item more
    than 10 times.

    This was choosen so we can more efficiently generate recommendations on a
    single machine.

    Also the data is partioned in 200k partitions so no out of memory error
    occurs.

    Parameters
    ----------
    Evaluation: {bool}
        Evaluates the model hyper-parameters in a random train-test split
    """
    spark = SparkSession.builder.appName(
        name="data-ingestion"
    ).config(
        "spark.executor.memory", "2GB"
    ).config("spark.driver.memory", "8G").getOrCreate()

    n = 10

    user_item = spark.read.parquet(
        "/data_proj/intermediate/user_item.parquet").repartition(20000)
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
    user_recs = generate_recommendation(
        user_recs, user_model, product_model, n)

    browser_user = spark.read.parquet(
        "/data_proj/intermediate/user_browser_ids.parquet").repartition(20000)

    user_recs = browser_user.join(
        user_recs,
        user_recs.user_id == browser_user.user_id
    ).drop('user_id')

    print("saving    recommendations")
    user_recs.write.json("/data_proj/output/recommendations")


def indexer(user_item):
    """Apply StringIndexer to the user_id and product_id columns,
    and returns the fitted indexer

    Parameter
    ---------
    user_item: {data_frame}
        PySpark DataFrame containing the user item score.

    Returns
    -------
    user_model: {object}
        StringToIndex fitted model on the user_id column.
    product_model: {object}
        StringToIndex fitted model on the product_id column.
    user_item: {data_frame}
        PySpark DataFrame containing the indexed user item score.

    """
    user_item, user_model = indexer_fit_transform(user_item, "user_id")
    user_item, product_model = indexer_fit_transform(user_item, "product_id")
    return user_model, product_model, user_item


def indexer_fit_transform(user_item, col_name):
    """ Fit and transform a given column to and integer index.

    Parameters
    ----------
    user_item: {data_frame}
        User item data frame.
    col_name: {string}

    Returns
    -------
    user_item: {data_frame}
        User item data frame.
    model: {string}
        Fitted stringIndexer.
    """
    indexed_col = col_name + '_ind'
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
    """ Fit Implicit ALS Recommender Model to infer recommendations for
    products on users.

    Parameter
    ---------
    user_item: {data frame}
        User item data frame.

    Returns
    -------
        Fitted ALS model object.

    """
    als = ALS(
        maxIter=10, regParam=0.2, userCol="user_id_ind",
        numUserBlocks=20000, numItemBlocks=20000,
        itemCol="product_id_ind", ratingCol="score",
        coldStartStrategy="drop", implicitPrefs=True,
        checkpointInterval=2
    )
    user_item = user_item.repartition(20000)
    return als.fit(user_item)


def generate_recommendation(user_recs, user_model, product_model, n):
    """ Creates recommendation data frame, coded and using the proper ids.

    Parameters
    ----------
    user_recs: {data frame}
        User recommendation matrix.

    user_model: {object}
        user_id indexer model

    product_model: {object}
        product_id indexer model

    Returns:
    --------
        Treated and modified recommendation data.

    """
    user_id_to_label = IndexToString(
        inputCol="user_id_ind", outputCol="user_id", labels=user_model.labels)
    user_recs = user_id_to_label.transform(user_recs).drop('user_id_ind')

    product_labels_ = array(*[lit(x) for x in product_model.labels])
    recommendations = array(
        *[when(col("recommendations")[i]["rating"] > 0,
               product_labels_[col("recommendations")[
                   i]["product_id_ind"]].alias("product_id")
               )for i in range(n)])

    return user_recs.withColumn(
        "items", recommendations).drop("recommendations")
