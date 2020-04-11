import json
from ap import db
from crypto_utils.conversions import SigConversion


class CPKeyModel(db.Model):
    timestamp_ = db.Column(db.Integer, primary_key=True)
    policy_ = db.Column(db.Integer, primary_key=True)
    public_key_ = db.Column(db.String)

    def __init__(self, timestamp, policy, public_key):
        self.timestamp_ = timestamp
        self.policy_ = policy
        self.public_key_ = public_key

    def __repr__(self):
        return "<Key(timestamp='%s', policy='%s', pub_key='%s')>" % (self.timestamp, self.policy, self.public_key_)

    def __str__(self):
        return "CPKeyModel: {}, {}, {}".format(self.timestamp, self.policy, self.public_key_)

    @property
    def public_key(self):
        key_str = json.loads(self.public_key_)
        return SigConversion.convert_dict_modint(key_str)

    @property
    def timestamp(self):
        return self.timestamp_

    @property
    def policy(self):
        return self.policy_

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def find(timestamp: int, policy: int):
        tmp = CPKeyModel.query.get((timestamp, policy))
        if tmp:
            return tmp
        else:
            return None

