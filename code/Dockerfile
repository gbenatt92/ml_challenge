FROM gettyimages/spark:2.2.0-hadoop-2.7

MAINTAINER Gabriel Alvim <gabriel.b.alvim@gmail.com>


RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y;\
    apt-get install build-essential libssl-dev libffi-dev python3-dev -y


RUN set -eux; \
    pip3 install Cython==0.27.2; \
    pip3 install scipy; \
    pip3 install implicit==0.2.7

ADD . /app

RUN set -eux; \
    cd /app/; \
    pip3 install .

ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

ENTRYPOINT ["python3", "/app/main.py"]
