## code_base has all the dependencies installed
#FROM code_latest

# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /cp
WORKDIR /code

RUN pip install apscheduler

# Copy the current directory contents into the container at /cp
ADD ./ap ./ap
ADD ./crypto_utils ./crypto_utils

CMD ["gunicorn","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","ap:create_app()"]