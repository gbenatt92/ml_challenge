# Machine Learning Challenge

By Gabriel Alvim

## Summary

This challenge documentation is divided in the following 4 parts

* [Infrastructure](docs/INFRASTRUCTURE.md)
* [Algorithm](docs/ALGORITHM.md)
* [Evaluation](docs/EVALUATION.md)
* [API](docs/API.md)

Everything is run inside a Docker container using Python and PySpark. 

## Requirements

To run this project it's required to have both [Docker](https://www.docker.com/community-edition) and [pixz](https://github.com/vasi/pixz) installed.

## Set up

To set up this project run the following in order

### 1. Docker Image build.

```bash
make build
```


### 2. Download and decompress required files.

```bash
make download
```

### 3. Data Ingestion

```bash
make data-ingestion
```

### 4. Generate Recommendations

```bash
make rec-train
```

If you want to evaluate before hand as well, please run the following

```bash
make rec-evaluate
```

## TODO's

There is a list of improvements to be made right over [here](TODO.md). These couldn't make the cut due to time constraints but are listed for the sake of transparency.
