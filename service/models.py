from flask_login import UserMixin
from service import db


class User(UserMixin, db.Model):
    y = db.Column(db.String(256), primary_key=True)

    def __init__(self, y):
        self.y = y

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()