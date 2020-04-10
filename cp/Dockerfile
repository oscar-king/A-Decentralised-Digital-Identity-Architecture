# code_base has all the dependencies installed
FROM code_latest

# Set the working directory to /app
WORKDIR /cp

# Copy the current directory contents into the container at /app
ADD . ./

# Run flask in dev mode
RUN export FLASK_APP=app.py

#RUN pip install gunicorn

CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["gunicorn", "--workers=2", "--bind=:80","--forwarded-allow-ips=*","cp:create_app()"]