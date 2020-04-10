from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# init SQLAlchemy so we can use it later in our models
from sqlalchemy.pool import StaticPool

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ap.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_SECRET_KEY'] = '234rfae23rsefaw3235saex3'
    app.config['JWT_BLACKLIST_ENABLED'] = False
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool
    }

    db.init_app(app)
    jwt.init_app(app)

    from ap.models.Session import Session

    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        return Session.query.get(identity)

    db.create_all(app=app)
    return app