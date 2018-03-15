FROM gettyimages/spark:2.2.0-hadoop-2.7

MAINTAINER Gabriel Alvim <gabriel.b.alvim@gmail.com>


RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y;\
    apt-get install build-essential libssl-dev libffi-dev python3-dev -y


ADD . /app

RUN set -eux; \
    cd /app/; \
    pip3 install .

ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

ENV LD_LIBRARY_PATH=/usr/local/hadoop/lib/native/:$LD_LIBRARY_PATH

ENTRYPOINT ["python3", "/app/main.py"]
