# init.py

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import StaticPool

# init SQLAlchemy so we can use it later in our models

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cp.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool
    }

    app.config['JWT_SECRET_KEY'] = '234rfae23rsefaw3235saex3'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    app.config['CP_REST_URI'] = 'http://cp_rest_api:3000'
    app.config['CP_DLT_ID'] = "2000"

    from cp.models.RevokedTokenModel import RevokedTokenModel

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return RevokedTokenModel.is_jti_blacklisted(jti)

    db.init_app(app)
    jwt.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from cp.models.UserModel import UserModel

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return UserModel.query.get(int(user_id))

    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        return UserModel.query.get(identity)

    # blueprint for auth routes in our app
    from cp.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from cp.main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    db.create_all(app=app)
    return app
