import json

from cp import db
from sqlalchemy import ForeignKey

from crypto_utils.conversions import SigConversion


class SigVarsModel(db.Model):
    __tablename__ = 'sigvars'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    policy = db.Column(db.Integer)
    u_ = db.Column(db.String)
    d_ = db.Column(db.String)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, timestamp, policy, u, d, user_id):
        """
        :param timestamp: POSIX timestamp
        :param policy: integer referencing the policy chosen
        :param u: Element.Integer mod p
        :param d: Element.Integer mod p
        :param user_id: integer representing the user in the CP's system database
        """
        self.timestamp = timestamp
        self.policy = policy
        self.user_id = user_id
        self.u_ = SigConversion.modint2strlist(u)
        self.d_ = SigConversion.modint2strlist(d)

    def __repr__(self):
        return "<UserSigVars(user_id='%s', u='%s', d='%s')>" % (self.user_id, self.u, self.d)

    @property
    def u(self):
        return SigConversion.strlist2modint(self.u_)

    @property
    def d(self):
        return SigConversion.strlist2modint(self.d_)

    @property
    def get_timestamp(self):
        return self.timestamp

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
