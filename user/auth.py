# auth.py
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import current_app
from user.models.sessions import SessionModel

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

    res = requests.post("http://{}/login".format(current_app.config['cp_host']), json=data)
    data = res.json()
    if res.status_code == 200:
        SessionModel.delete()
        SessionModel(access_token=data.get('access'),
                     refresh_token=data.get('refresh')).save()
        return redirect(url_for('main.gen_keys'))
    else:
        flash(data.get('message'), 'login')
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

    res = requests.post("http://{}/signup".format(current_app.config['cp_host']), json=data)

    data = res.json()
    if res.status_code == 201:
        return redirect(url_for('auth.login'))
    else:
        flash(data.get('message'), 'signup')
        return render_template('signup.html')


@auth.route('/logout')
def logout():
    first = SessionModel.query.first()
    if first:
        access_token = SessionModel.query.first().access_token
        headers = {
            'Authorization': "Bearer " + access_token
        }
        res = requests.delete("http://{}/logout".format(current_app.config['cp_host']), headers=headers)
        if res.status_code == 200:
            return redirect(url_for('auth.login'))
        else:
            flash(res.json().get('message'))
            return redirect(url_for('main.index'))
    else:
        return redirect(url_for('auth.login'))
