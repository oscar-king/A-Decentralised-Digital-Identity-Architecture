import os

import requests
from flask import json, jsonify, request
from service import host
from crypto_utils.conversions import SigConversion
from service import create_app, db
from service.handlers import request_handler, verify_sig
from service.models import User

app = create_app()


@app.route("/")
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container."

    return "Hello from Service"


@app.route("/request")
def request_y():
    y = request_handler()
    return jsonify({'y': y}), 201


@app.route("/response", methods=['POST'])
def user_response():
    data = json.loads(request.json)

    params = {
        'policy': data.get('policy'),
        'timestamp': data.get('timestamp')
    }

    # Find y in database
    user = User.query.get(data.get('y'))
    if user is None:
        return jsonify({'message': 'Could not find y'}), 500

    # TODO: Ideally the keys should have been distributed by some other means
    res = requests.get('http://%s:5001/pubkey' % host, params=params)
    if res.status_code == 200:
        key = res.json()
        key = SigConversion.convert_dict_modint(key)
        sig = json.loads(data.get('sig'))
        sig = SigConversion.convert_dict_modint(sig)
        if verify_sig(key, sig, data.get('y')):
            return jsonify({'message': 'Success'}), 200
        else:
            return jsonify({'message': 'Could not verify signature'}), 500


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
    app.run()
