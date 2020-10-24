## code_base has all the dependencies installed
#FROM code_latest
#
## Set the working directory to /app
#WORKDIR /user
#
## Copy the current directory contents into the container at /app
#ADD . ./
#
## Run flask in dev mode
#RUN export FLASK_APP=app.py
#RUN pip install gunicorn
#
##CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["gunicorn", "--chdir=/user","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","app:user_gunicorn"]

# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /code
WORKDIR /code

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir psycopg2-binary

# Copy the current directory contents into the container at /user
ADD ./user ./user
ADD ./crypto_utils ./crypto_utils

CMD ["gunicorn","--workers=3", "--bind=:5000","--forwarded-allow-ips=*","--log-level=info", "user:create_app()"]