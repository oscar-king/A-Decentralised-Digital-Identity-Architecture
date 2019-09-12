from flask_login import UserMixin
from ap import db


class UserNonce(UserMixin, db.Model):
    y = db.Column(db.String(256), primary_key=True)
    pubk = db.Column(db.String(), nullable=False)

    def __init__(self, y, pubk):
        self.y = y
        self.pubk = pubk

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def find(self, y):
        tmp = UserNonce.query.get(y)
        if tmp:
            self.y = tmp.y
            self.pubk = tmp.pubk
            return tmp
        else:
            return None

