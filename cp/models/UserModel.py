# UserModel.py

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


from cp import db


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    sigvars = relationship('SigVarsModel')

    def get_id(self):
        return self.id

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.hash_password(password)

    def __repr__(self):
        return "<User(name='%s', email='%s')>" % (self.name, self.email)

    def hash_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_sigvar(self, timestamp, policy):
        for x in self.sigvars:
            if x.timestamp == timestamp and x.policy == policy:
                return x
        return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
