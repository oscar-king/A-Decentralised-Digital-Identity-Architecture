from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
# ap_host = "ap:5000"


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///service.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ap_host'] = 'ap:5000'

    # blueprint for non-auth parts of app
    from service.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.init_app(app)

    db.create_all(app=app)

    return app
