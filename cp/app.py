import os

import flask
from flask import Flask

from cp.workers import post_key_worker

app = Flask(__name__)


@app.route("/")
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container behind nginx!"

    return "Hello from Flask"


@app.route("/identify", methods=['GET', 'POST'])
def identify():
    return "CP identification stub -> will be a post"


@app.route("/post_keys", methods=['GET', 'POST'])
def post_keys():
    if flask.request.method == 'POST':
        worker = post_key_worker.PostKeyWorker(1)
        worker.schedule_key_publishing("Key", ["This", "is", "a", "test"])
        return "Okay"
    elif flask.request.method == 'GET':
        return "This is a POST method"


if __name__ == '__main__':
    app.run()
