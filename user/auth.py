# auth.py
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash, json
from user.models import SessionModel


auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    data = {
        'email':request.form.get('email'),
        'password': request.form.get('password'),
        'remember': request.form.get('remember')
    }

    res = requests.post("http://127.0.0.1:5002/login", json=json.dumps(data))
    data = res.json()
    if res.status_code == 200:
        SessionModel(access_token=data.get('access'),
                     refresh_token=data.get('refresh')).save()
        return redirect(url_for('main.gen_keys'))
    else:
        flash(data.get('content'), 'login')
        return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    data = {
        'email': request.form.get('email'),
        'name': request.form.get('name'),
        'password': request.form.get('password')
    }
    #
    # if user: # if a user is found, we want to redirect back to signup page so user can try again
    #     flash('Email address already exists', 'signup')
    #     return redirect(url_for('auth.signup'))


    return redirect(url_for('auth.login'))


@auth.route('/logout', methods=['DELETE'])
def logout():
    return redirect(url_for('main.index'))