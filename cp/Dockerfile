# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /cp
WORKDIR /code

# Copy the current directory contents into the container at /cp
ADD ./cp ./cp
ADD ./crypto_utils ./crypto_utils

#CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
CMD ["gunicorn","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","cp:create_app()"]