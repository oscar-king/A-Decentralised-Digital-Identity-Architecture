import os

import requests
from flask import json, jsonify, request, current_app, Blueprint
from crypto_utils.conversions import SigConversion
from service import db
from service.handlers import request_handler, verify_sig
from service.handlers import User
from service.utils import get_ap_key

main = Blueprint('main', __name__, template_folder='templates')

@main.route("/")
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")

    if app_name:
        return f"Hello from {app_name} running in a Docker container."

    return "Hello from Service"


@main.route("/request")
def request_y():
    y = request_handler()
    return jsonify({'y': y}), 201


@main.route("/response", methods=['POST'])
def user_response():
    data = json.loads(request.json)

    # params = {
    #     'policy': data.get('policy'),
    #     'timestamp': data.get('timestamp')
    # }
    policy = data.get('policy')
    timestamp = data.get('timestamp')

    # Find y in database
    user = User.query.get(data.get('y'))
    if user is None:
        return jsonify({'message': 'Could not find y'}), 500

    key = get_ap_key(timestamp, policy)
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
@main.route("/purge")
def purge_db():
    db.session.query(User).delete()
    db.session.commit()
    return "Purged", 200


@main.route("/db")
def show_all():
    data = []
    for user in User.query.order_by(User.y).all():
        data.append(user.y)
    return json.dumps(data)
