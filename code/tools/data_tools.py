from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, explode


def data_processing():
    """Runs and saves a series of data processing task to a bunch of parquet
    files.
    """
    spark = SparkSession.builder.appName(
        name="data-ingestion"
    ).config(
        "spark.executor.memory", "2G"
    ).config("spark.driver.memory", "10G").getOrCreate()

    views = spark.read.format("json").load("/data_proj/pdpviews.ndjson")
    transactions = spark.read.format("json").load(
        "/data_proj/transactions.ndjson")

    save_ids(views, transactions)

    create_user_item_dataframe(views, transactions)


def create_user_item_dataframe(views, transactions):
    """ Create the user item file and save it to parquet.

    Parameter
    ---------
    views: {object}
        A PySpark data frame containing a product view of a given browser.
    transactions: {object}
        A PySpark data frame containing a product transaction of a given
        browser.
    """
    views = scorer(views, 1)
    views = create_user_product_agg(views)

    transactions = treating_items(transactions)
    transactions = scorer(transactions, 10)
    transactions = create_user_product_agg(transactions)

    total = views.union(transactions)
    total = create_user_product_agg(total).orderBy('score')

    total.describe(['score']).show()

    total.write.mode("overwrite").parquet(
        '/data_proj/intermediate/user_item.parquet')


def get_ids(data_frame):
    """ Retrieves the distinct relation of user_id and browser_id.

    Parameter
    ---------
    data_frame: {object}
        A PySpark data frame containing a browser_id and a user_id column.

    Returns
    -------
    data_frame: {object}
        A PySpark data frame composed of a distinct relation between a
        browser_id and a user_id column.
    """
    return data_frame.select('user_id', 'browser_id').distinct()


def scorer(data_frame, score):
    """ Adds a score column to the data.

    Parameters
    ----------
    data_frame: {object}
        A PySpark data frame.
    score: {int}
        A positive int number representing an arbitrary score.

    Returns
    -------
    data_frame: {object}
        A PySpark data frame with a score column.
    """

    return data_frame.withColumn(
        "score",
        lit(score).cast("integer")
    )


def save_ids(views, transactions):
    """ Retrieves the distinct relation of user_id and browser_id and saves them
    to a parquet file.

    Parameter
    ---------
    views: {object}
        A PySpark data frame containing a product view of a given browser.
    transactions: {object}
        A PySpark data frame containing a product transaction of a given
        browser.
    """
    ids_views = get_ids(views)
    ids_transactions = get_ids(transactions)

    ids = ids_views.union(ids_transactions)

    ids = ids.select(
        'user_id', 'browser_id').distinct()

    ids.write.mode("overwrite").parquet(
        '/data_proj/intermediate/user_browser_ids.parquet')


def treating_items(transactions):
    """ Treats the items array to return a data_frame containing the relation
    of product_id purchased and user_id.

    Parameter
    ---------
    transactions: {object}
        A PySpark data frame containing a product transaction of a given
        browser.

    Returns
    -------
    data_frame: {object}
        A PySpark data frame composed of a distinct relation between a
        a user_id and a product_id column.
    """

    transactions = transactions.select('user_id', 'items').withColumn(
        "product_id",
        explode(col("items"))
    )
    return transactions.withColumn(
        "product_id",
        col("product_id").getField("product_id")
    ).drop("items").distinct()


def create_user_product_agg(data_frame):
    return data_frame.groupBy(
        "user_id", "product_id"
    ).agg({"score": "sum"}).withColumnRenamed('sum(score)', "score")
