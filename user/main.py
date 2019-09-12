import functools

import flask
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, json
import os

from user.models import SessionModel
from user.utils.key_utils import generate_keys, blind_keys, blind_number

main = Blueprint('main', __name__, template_folder='templates')


def token_required(func):
    @functools.wraps(func)
    def decorator_token_required(*args, **kwargs):
        # Get access_token
        first = SessionModel.query.first()
        headers = {}
        if first:
            access_token = SessionModel.query.first().access_token
            headers = {
                'Authorization': "Bearer " + access_token
            }
        return func(headers)
    return decorator_token_required


@main.route('/')
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "User Interface"

    return render_template('index.html', name=app_name)


# TODO add expiry checking
@main.route('/generate_keys')
def gen_keys():
    access_token = SessionModel.query.first()
    if access_token is None:
        return redirect(url_for('auth.login'))
    return render_template('generate_keys.html')


# TODO Save keys on the user side
@main.route("/generate_keys", methods=['POST'])
@token_required
def generate_keys_post(headers):
    # Get the number of requested keys from the form, then generate the required number
    number = request.form.get('number')
    pubk, privk = generate_keys(number)

    # Blind the keys
    bpubk, privk = blind_keys(pubk, privk)

    # Post keys to CP
    try:
        res = requests.post("http://127.0.0.1:5002/post_keys", data=bpubk, headers=headers)
        if res.status_code == 201:
            # Need to add save functionality here
            return redirect(url_for('main.thanks'))
        else:
            return render_template('generate_keys.html')
    except Exception:
        return "Something went wrong with the post"


@main.route("/access_service", methods=['GET'])
def access_service():
    return render_template('service_authenticate.html')


@main.route("/access_service")
def access_service_post():
    # Get nonce from service
    y = requests.get("http://127.0.0.1:5003/request")

    # Blind nonce
    blinded_y = blind_number(y)

    # Request-certs CP_i

    # Prove-owner x_i

    # Request CP_i(x_i), blinded_y

    pass


@main.route("/request_cert")
def request_cert():
    # Get oldest key interval

    pass


@main.route('/thanks')
def thanks():
    return render_template('thanks.html')