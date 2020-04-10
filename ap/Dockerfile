## code_base has all the dependencies installed
#FROM code_latest
#
## Set the working directory to /app
#WORKDIR /ap
#
## Copy the current directory contents into the container at /app
#ADD . ./
#
## run the command to start uWSGI
##CMD ["waitress-serve", "--port=5001" ,"--call", "ap:create_app"]
#
## Run flask in dev mode
#RUN export FLASK_APP=app.py
#RUN pip install gunicorn
#
#
##CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["gunicorn","--chdir=/ap","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","app:app"]

# code_base has all the dependencies installed
FROM test_latest

# Set the working directory to /cp
WORKDIR /code

# Copy the current directory contents into the container at /cp
ADD ./ap ./ap
ADD ./crypto_utils ./crypto_utils

CMD ["gunicorn","--workers=2", "--bind=:5000","--forwarded-allow-ips=*","ap:create_app()"]