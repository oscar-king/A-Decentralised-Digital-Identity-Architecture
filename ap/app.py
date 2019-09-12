import os
from flask import Flask, request, Response, json

from ap.models import UserNonce
from ap.utils.ledger_utils import get_certs
from ap import db, create_app
from ap.utils.random import Nonce

app = create_app()


@app.route("/")
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container behind nginx!"

    return "Hello from Flask"


# TODO implement get_certs
@app.route("/request_certs", methods=['GET'])
def request_certs():
    cp = request.args.get('cp')
    timestamp = request.args.get('timestamp')

    if (cp is None) or (timestamp is None):
        return Response("Bad Request: Required parameters are not set.", status=400, mimetype='application/json')

    return Response(get_certs(cp, timestamp), status=200, mimetype='application/json')


@app.route("/prove_owner", methods=['GET', 'POST'])
def prove_owner():

    # Challenge
    if request.method == 'GET':
        pubk = request.args.get('pubk')
        if pubk is None:
            return Response("Bad Request: Required parameters are not set.", status=400, mimetype='application/json')
        else:
            nonce = Nonce(pubk).save()
            if nonce:
                return nonce, 201
            else:
                return Response("{'content': 'Something went wrong saving session info.'}",
                                status=501, mimetype='application/json')

    # Response
    elif request.method == 'POST':
        if not request.is_json:
            return Response("Bad Request: No data.", status=400, mimetype='application/json')
        else:
            data = json.loads(request.get_json())

            # Get data from db
            userNonce = UserNonce()



@app.route("/request_sig", methods=['POST'])
def request_sig():
    return "Need to implement this"


@app.before_first_request
def create_db():
    db.create_all(app=app)


if __name__ == '__main__':
    app.run()
