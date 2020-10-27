# init.py
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# init SQLAlchemy so we can use it later in our models
from sqlalchemy.exc import IntegrityError, OperationalError

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:root@user_db:5432/db'


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['cp_host'] = 'cp:5000'
    app.config['ap_host'] = 'ap:5000'
    app.config['service_host'] = 'service:5000'
    app.config['cp_dlt_id'] = 2000
    app.config['ap_dlt_id'] = 3000

    db.init_app(app)

    # blueprint for auth routes in our app
    from user.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from user.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    try:
        db.create_all(app=app)
    except (IntegrityError, OperationalError):
        print("db already exists.")

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    return app