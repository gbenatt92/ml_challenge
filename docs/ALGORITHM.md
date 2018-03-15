# Algorithm

The current Recommender System algorithm used is the [Alternating Least Squares as implemented by the Spark ML framework](https://spark.apache.org/docs/2.1.0/ml-collaborative-filtering.html).

## Job logic

The whole job was divided in 2 steps

### Feature Engineering

The data came in 2 files, one huge and one not so huge, the first problem then was assimilating implicit information from both data sets and creating the item-user matrix.

Some decisions were made on the basis of intuition and others were made while doing research on the matter. 

I've decided to consider only the relation between user_id and product_id. 

Although it's required to give an input based on the browser_id, a better recommendation is aggregated when consider the user, since they can access the store on any device.

The driver behind many of the decisions are due to a large amount of data, lack of resources and lack of time.

Another decision made here is to give the score to views on a product as 1 and sum them by user-product, and the score to distinct purchases as 10. 

The logic behind this approach comes from the fact that although views do indicate an interest of an user, it's not as strong of an information as a purchase. The numbers represents this intuition.

While the reason for only counting distinct purchases is to avoid weighting certain types of products more and to avoid having to analyze and weight quantity versus price.

This approach loses a lot of information, but it does make this step on such large data much easier and faster.

### Recommender System

The recommender system runs only on the item-user relationship that has a score of 10 or above, meaning either 10 distinct views or at least 1 purchase. The choice was made so more accurate recommendations can be given while still having views as an input.

The Recommender System of choice was the Implicit Alternating Least Squares as is implemented by Spark. The system consists of a block approach that allows for matrix factorization to occur in parallel.

By being implicit it means that the scores given previously are converted into a preference matrix P, where if the score > 0 the element in P is 1 and 0 otherwise. From the documentation: "The ratings then act as ‘confidence’ values related to strength of indicated user preferences rather than explicit ratings given to items."


## Parameters choice 

The choice of the parameters given was made for both performance wise and after a few evaluations based on random sampled train-test splits.

A better approach would be using cross-validation and optimization algorithm on the hyper-parameters, but parallelizing it would be too costly in terms of development time. 

On past projects of mine, I've been having good results using Bayesian Optimization on Gaussian Processes, since it's robust to non-convex optimization space and can be rather fast to tune (faster than grid search when there are too many parameters).

The current parameters of choice are the following

* maxIter=10
* regParam=0.2
* numUserBlocks=20000 
* numItemBlocks=20000
* coldStartStrategy="drop"
* implicitPrefs=True
* checkpointInterval=2

## Recommendations output file

The output file doesn't contain recommendation for all users and items. A 10% sample was used to generate it. But given a proper Spark Cluster, scaling this job to the entire seen population would be no problem.

The file is as specified and contains up to 10 recommendations of items with predicted score above 0 for each browser_id, although it will be repeated if it contains to the same user_id.
