from flask_login import UserMixin
from service import db


class User(UserMixin, db.Model):
    y = db.Column(db.String(256), primary_key=True)
