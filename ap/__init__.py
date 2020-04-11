from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_jwt_extended import JWTManager
from pytz import utc


# init SQLAlchemy so we can use it later in our models
from sqlalchemy.pool import StaticPool

db = SQLAlchemy()
jwt = JWTManager()

# Schedule background job to publish policies
scheduler = BackgroundScheduler(timezone=utc)

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ap.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_SECRET_KEY'] = '234rfae23rsefaw3235saex3'
    app.config['JWT_BLACKLIST_ENABLED'] = False
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['SCHEDULER_TIMEZONE'] = utc
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

    # blueprint for non-auth parts of app
    from ap.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.create_all(app=app)

    # Automatically cache CP public keys
    from ap.utils.ledger_utils import cache_cp_pubkey
    job = scheduler.add_job(cache_cp_pubkey, 'interval', [app], seconds=10)
    scheduler.start()

    return app