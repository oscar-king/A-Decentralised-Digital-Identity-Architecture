# code_base has all the dependencies installed
FROM code_latest

# Set the working directory to /app
WORKDIR /service

# Copy the current directory contents into the container at /app
ADD service /service
ADD .env /service

#RUN pip uninstall -y uwsgi && apk add pcre pcre-dev libressl-dev libffi-dev && pip install uwsgi -I --no-cache-dir \
#    && pip install wheel && python setup.py bdist_wheel && pip install dist/ap-0.0.1-py3-none-any.whl \
#     && export FLASK_APP=cp && pip install waitress

# run the command to start uWSGI
#CMD ["waitress-serve", "--port=5002" ,"--call", "cp:create_app"]

# Run flask in dev mode
RUN export FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]
