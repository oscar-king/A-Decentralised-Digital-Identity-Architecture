import os
from service import create_app, db
from flask import Flask, json

from service.handlers import request_handler
from service.models import User

app = create_app()


@app.route("/")
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container behind nginx!"

    return "Hello from Flask"


@app.route("/request")
def request():
    y = request_handler()
    return json.dumps(y), 201


# TODO Need to implement this
@app.route("/response")
def response():
    return "TODO"

"""
    The following two view functions are for development only
        1. purge_db
        2. db
"""
@app.route("/purge")
def purge_db():
    db.session.query(User).delete()
    db.session.commit()
    return "Purged", 200


@app.route("/db")
def show_all():
    data = []
    for user in User.query.order_by(User.y).all():
        data.append(user.y)
    return json.dumps(data)


if __name__ == '__main__':
    db.create_all(app=app)
    app.run(port=5003)
