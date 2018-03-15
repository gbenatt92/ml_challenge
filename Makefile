img_name := gbenatt92/ml-test
tag_name := 0.0.1

build:
	set -eux; \
	cd code/; \
	docker build --network=host -t $(img_name):latest .

build-realease:	
	set -eux; \
	cd code/; \
	docker build --network=host -t $(img_name):$(tag_name) .

download:
	set -eux; \
	mkdir data; \
	cd data/; \
	wget https://s3.amazonaws.com/ml-challenge/transactions.ndjson.xz; \
	wget https://s3.amazonaws.com/ml-challenge/pdpviews.ndjson.xz; \
	mkdir intermediate; \
	pixz -d pdpviews.ndjson.xz; \
	pixz -d transactions.ndjson.xz

data-ingestion:
	set -eux; \
	docker run -it -v `pwd`/data:/data_proj $(img_name):latest -d