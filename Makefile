img_name := gbenatt92/ml-challenge
tag_name := 0.0.1

dowload:
	set -eux; \
    wget https://s3.amazonaws.com/ml-challenge/transactions.ndjson.xz; \
    wget https://s3.amazonaws.com/ml-challenge/pdpviews.ndjson.xz

build:
    docker build --network=host -t $(img_name):latest .


