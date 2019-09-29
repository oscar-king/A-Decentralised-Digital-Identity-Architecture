import json

from charm.toolbox.conversion import Conversion
from sqlalchemy import ForeignKey, JSON
from cp import db
from _md5 import md5


class PolicyPoolModel(db.Model):
    policy = db.Column(db.Integer, ForeignKey('policies.policy'), primary_key=True)
    timestamp = db.Column(db.Integer, primary_key=True)
    pool_ = db.Column(JSON)

    def __init__(self, policy: int, timestamp: int):
        self.policy = policy
        self.timestamp = timestamp
        self.pool_ = []

    def __hash__(self):
        return Conversion.OS2IP(md5(json.dumps(self.pool).encode()).digest())

    @property
    def pool(self):
        res = list()
        pool = json.loads(self.pool_)
        for x in pool:
            data = {
              "$class": "digid.Proof",
              "hash": Conversion.OS2IP(md5(x.encode()).digest()),
              "proofs": x
            }
            res.append(data)
        return res

    @pool.setter
    def pool(self, proofs: dict):
        self.append(proofs)

    def append(self, proofs: dict):
        tmp = json.loads(str(self.pool_))
        tmp.append(json.dumps(proofs))
        self.pool_ = json.dumps(tmp)
        self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()