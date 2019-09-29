# auth.py
from datetime import timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash, Response, json, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_csrf_token, set_access_cookies, \
    set_refresh_cookies, unset_jwt_cookies, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from flask_login import login_user, logout_user
from cp.models.RevokedTokenModel import RevokedTokenModel
from cp.models.UserModel import UserModel

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['POST'])
def login_post():
    data = json.loads(request.json)

    email = data.get('email')
    password = data.get('password')
    remember = True if data.get('remember') else False

    user = UserModel.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        flash('Please check your login details and try again.', 'login')
        # return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page
        return jsonify({'message': 'Please check your login details and try again.'}), 401

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(minutes=30))

    resp = jsonify({
        'message': 'Logged in as {}'.format(user.email),
        'access': access_token,
        'refresh': refresh_token
    })

    return resp, 200


@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the access JWT and CSRF double submit protection cookies
    # in this response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@auth.route('/signup', methods=['POST'])
def signup_post():
    data = json.loads(request.json)

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    # if this returns a user, then the email already exists in database
    user = UserModel.query.filter_by(email=email).first()

    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        return jsonify({'message': 'User already exists.'}), 401

    # create new user with the form data. Password is hashed automatically.
    new_user = UserModel(email=email, name=name, password=password)

    # add the new user to the database
    new_user.save_to_db()

    return jsonify({'message': 'Created.'}), 201


@auth.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    try:
        # Revoke
        RevokedTokenModel(jti=jti).save_to_db()

        # Unset cookies
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        logout_user()
        return resp, 200
    except:
        return {'message': 'Something went wrong'}, 500


@auth.route('/logout_refresh', methods=['DELETE'])
@jwt_refresh_token_required
def logout_refresh():
    jti = get_raw_jwt()['jti']
    try:
        # Revoke
        RevokedTokenModel(jti=jti).save_to_db()

        # Unset cookies
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        logout_user()
        return resp, 200
    except:
        return {'message': 'Something went wrong'}, 500
