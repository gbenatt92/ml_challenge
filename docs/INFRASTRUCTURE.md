# Infrastructure

## Data ingestion

Here I describe how the data ingestion occurs on both the current setup and how it would occur in case of a POST API.

### Current Setup

Data is downloaded into the `data/` using `wget`. To replicte easily step you can simply run. 

``` bash
make download
```

Keep in mind that it downloads 1.9GB of files.

With the files in the local folder, and the project properly setup, conversion of the compressed ndjson files can be ran with

```bash
python main.py -d
``` 

This step not only decompress the `.ndjson.xz` files, but it also saves them as `.parquet` files in the `data/intermediate/` folder. They are compressed using SNAPPY compression, which allows for faster decompression.

Parquet files were used as an intermediate step so the Dask jobs can read from it faster and partioned, which in turn allows for better scalability both out of memory or accross multiple workers.

This is not parallel, so it does take a while to finish. An improvement would be to make a parallel set up for this ingestion.

### Post API

A Post API set up would be composed of 2 URLs, one for the pdpviews jsons and another for the transactions jsons. An ideal set up would be for it to be powered by Kafka, with each having its own stream processor. 

From the Kafka stream it would be much easier to convert them into parquet files and save them in a HDFS to be accessed by a Hive cluster.

Another advantage from using Kafka would be scalability and speed when receiving JSONs, it would allow the data to be ingested on many nodes and to be processed by many workers.

## Distributed processing 

This project uses Dask on Parquet files as a way to distribute the data processing. Although no Dask cluster was set up to make the recommendations, the process was optimized to run distributed on a single worker.

Currently these steps can be distributed on many workers:

* Preprocessing of the pdpviews.parquet.
* Parts of the preprocessing of the transactions.parquet.
* The concatenation of both processed data.

The recommendation algorithm itself is distributed accross multiple cores in a single machine using the Implicit package. This package is built on top of Cython and can also be ran on a GPU, although I personally didn't test yet.

## System architecture

Bellow is a flowchart describing the ideal system archtecture.

![Flowchart](images/ml_challenge_solution_archtecture.png)

* Data Ingestion: is as described previously
* Feature Engineering: uses a combination of Dask, Pandas and Scipy.
* Algorithm: will be discussed in more detail soon, but it currently uses implicity and outputs a `.ndjson.xz` files containing the recommendations.