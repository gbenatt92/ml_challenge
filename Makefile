img_name := gbenatt92/ml-test

build:
	set -eux; \
	cd code/; \
	docker build --network=host -t $(img_name):latest .

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
	docker run -it --rm -v `pwd`/data:/data_proj  -v `pwd`/code:/app  $(img_name):latest -d

rec-train:
	set -eux; \
	docker run -it --rm -v `pwd`/data:/data_proj  -v `pwd`/code:/app  $(img_name):latest -t

rec-evaluate:
	set -eux; \
	docker run -it --rm -v `pwd`/data:/data_proj  -v `pwd`/code:/app  $(img_name):latest -t -e
