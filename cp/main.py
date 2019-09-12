import flask
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, json, Response
from flask_jwt_extended import jwt_required
from flask_login import login_required, current_user
import os

from cp.models.UserModel import UserModel
from cp.workers import post_key_worker


main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "Certification Provider Interface"

    return render_template('index.html', name=app_name)


# TODO Return all active signatures
@main.route('/active_keys')
def get_keys():
    return json.dumps("This will be a list of active signatures")


@main.route('/users')
def get_users():
    user = []
    for x in UserModel.query.all():
        user.append(x.email)
    return str(user)


#TODO seems not to work
@main.route('/reset_users')
def reset_users():
    map(lambda x: x.delete(), UserModel.query.all())
    print()
    return redirect(url_for('main.get_users'))


@main.route('/post_keys')
@jwt_required
def post_keys():
    return render_template('post_keys.html')


# TODO Link up worker so that these keys are posted onto the blockchain. Return needs to be the (CP_1, and the interval)
@main.route("/post_keys", methods=['POST'])
@jwt_required
def post_keys_post():
    keys = request.get_data()

    if not keys: # If no file is submitted flash message
        flash('Please submit file', 'post_keys')
        # return redirect(url_for('main.post_keys'))
        return Response("{'content':Please check your form contents and try again.'}", status=501, mimetype='application/json')

    # worker = post_key_worker.PostKeyWorker(1)
    # worker.schedule_key_publishing("Key", ["This", "is", "a", "client_test"])
    # return redirect(url_for('main.thanks'))
    return Response("{'content':success'}", status=201,
                    mimetype='application/json')


@main.route('/thanks')
@jwt_required
def thanks():
    return render_template('thanks.html')