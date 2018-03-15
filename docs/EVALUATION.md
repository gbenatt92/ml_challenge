# Evaluation

## Choice of metrics

The metric of choice was the RMSE which should be minimized to achieve the best performance. 

The RMSE was chosen due to its easier calculation and my familiarity with analyzing it, but I confess it isn't the best metric for a implicit recommendation problem since the scores were arbitrary.

A better metric would be NDCG which measures the fitness of rank, so the more actual known interested items it recommends first, the better the metric. This is ideal in the scenario where we are actually measuring Preference and not a given rating or metric. 

There are a few problems with using NDCG though, it's a non differentiable metric thus making common optimization algorithms unsuited for it (such as the Gradient Descent) and it does takes a bit more time to compute as opposed to RMSE.


## Quality assurance and Feedback

The quality assurance would be given by a hold out split, if the evaluation is within a certain threshold the model is ok. This should be monitored whenever a new batch of data is given.

Another way of measuring quality would be to print an explanation for a given recommendation and make sure it makes sense. This would be more difficult to implement but would give a better approach.

This can be implemented for the user as well, a good explanation for the recommendation can give the user a better assurance when trusting the machine. A good example of this is how Spotify generates play-lists and recommends songs. 
