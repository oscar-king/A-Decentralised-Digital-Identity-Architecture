import flask
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
import os
from cp.workers import post_key_worker


main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def index():
    # Use os.getenv("key") to get environment variables
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "Hello from Flask"

    return render_template('index.html', name = app_name)


@main.route('/post_keys')
@login_required
def post_keys():
    return render_template('post_keys.html')


@main.route("/post_keys", methods=['POST'])
@login_required
def post_keys_post():
    keys = request.form.get('keys')

    if not keys: # If no file is submitted flash message
        flash('Please submit file', 'post_keys')
        return redirect(url_for('main.post_keys'))
    # worker = post_key_worker.PostKeyWorker(1)
    # worker.schedule_key_publishing("Key", ["This", "is", "a", "test"])
    return redirect(url_for('main.thanks'))


@main.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html')