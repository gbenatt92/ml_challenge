FROM daskdev/dask

MAINTAINER Gabriel Alvim <gabriel.b.alvim@gmail.com>

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y;\
    apt-get install build-essential -y

ADD . /app

RUN set -eux; \
    cd /app/; \
    pip install Cython==0.27.2; \
    pip install scipy; \
    pip install implicit==0.2.6; \
    pip install .

ENTRYPOINT ["python3","app/main.py"]
