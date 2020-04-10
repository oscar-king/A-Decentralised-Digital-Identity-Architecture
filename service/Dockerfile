## code_base has all the dependencies installed
#FROM code_latest
#
## Set the working directory to /app
#WORKDIR /service
#
## Copy the current directory contents into the container at /app
#ADD . ./
#
## Run flask in dev mode
#RUN export FLASK_APP=app.py
#
#
#RUN pip install gunicorn
#
#CMD ["flask", "run", "--host=0.0.0.0"]
##CMD ["gunicorn","--chdir=/service","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","app:app"]

# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /code
WORKDIR /code

# Copy the current directory contents into the container at /service
ADD ./service ./service
ADD ./crypto_utils ./crypto_utils

CMD ["gunicorn","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","service:create_app()"]