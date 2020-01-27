from sqlalchemy import ForeignKey

from cp import db
from crypto_utils.conversions import SigConversion


class SigVarsModel(db.Model):
    __tablename__ = 'sigvars'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    policy = db.Column(db.Integer)
    u_ = db.Column(db.String)
    d_ = db.Column(db.String)
    s1_ = db.Column(db.String)
    s2_ = db.Column(db.String)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, timestamp, policy, u, d, s1, s2, user_id):
        """
        :param timestamp: POSIX timestamp
        :param policy: integer referencing the policy chosen
        :param u: Element.Integer mod q
        :param d: Element.Integer mod q
        :param s1: Element.Integer mod q
        :param s2: Element.Integer mod q
        :param user_id: integer representing the user in the CP's system database
        """
        self.timestamp = timestamp
        self.policy = policy
        self.user_id = user_id
        self.u_ = SigConversion.modint2strlist(u)
        self.d_ = SigConversion.modint2strlist(d)
        self.s1_ = SigConversion.modint2strlist(s1)
        self.s2_ = SigConversion.modint2strlist(s2)

    def __repr__(self):
        return "<UserSigVars(user_id='%s', u='%s', d='%s', s1='%s', s2='%s')>" % \
               (self.user_id, self.u, self.d, self.s1, self.s2)

    @property
    def u(self):
        return SigConversion.strlist2modint(self.u_)

    @property
    def d(self):
        return SigConversion.strlist2modint(self.d_)

    @property
    def s1(self):
        return SigConversion.strlist2modint(self.s1_)

    @property
    def s2(self):
        return SigConversion.strlist2modint(self.s2_)

    @property
    def get_timestamp(self):
        return self.timestamp

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
