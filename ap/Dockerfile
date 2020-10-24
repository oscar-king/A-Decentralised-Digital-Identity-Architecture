## code_base has all the dependencies installed
#FROM code_latest

# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /cp
WORKDIR /code

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir apscheduler psycopg2-binary
#    && apk del --no-cache .build-deps

# Copy the current directory contents into the container at /cp
ADD ./ap ./ap
ADD ./crypto_utils ./crypto_utils

CMD ["gunicorn","--workers=3", "--bind=:5000","--forwarded-allow-ips=*","ap:create_app()"]