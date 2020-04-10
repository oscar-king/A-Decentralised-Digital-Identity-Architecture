# Use the Python3.7-alpine image for smaller image size
FROM python:3.7-alpine

RUN apk update && apk add --no-cache --virtual .build-deps xz flex bison git wget make \
    && apk add build-base pcre pcre-dev libressl-dev libffi-dev \
    && wget https://gmplib.org/download/gmp/gmp-6.1.2.tar.xz && tar -xf gmp-6.1.2.tar.xz && cd gmp-6.1.2 \
    && ./configure && make && make check && make install && cd .. && rm gmp-6.1.2.tar.xz \
    && wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && tar xzf pbc-0.5.14.tar.gz && cd pbc-0.5.14 \
    && ./configure && make && make install && cd .. && rm pbc-0.5.14.tar.gz

# make test isn't run because it is failing for certain schemes - these schemes aren't all required so these errors are ignored.
RUN git clone https://github.com/JHUISI/charm.git && cd charm && ./configure.sh && make && make install \
    && cd .. && rm -r charm

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && apk del .build-deps && rm requirements.txt

RUN which python3
CMD ["python3"]