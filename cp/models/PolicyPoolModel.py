import json
import sys

from Crypto.Hash.SHA256 import SHA256Hash
from charm.toolbox.conversion import Conversion
from sqlalchemy import ForeignKey, JSON
from cp import db


class PolicyPoolModel(db.Model):
    policy = db.Column(db.Integer, ForeignKey('policies.policy'), primary_key=True)
    timestamp = db.Column(db.Integer, primary_key=True)
    pool_ = db.Column(JSON)

    def __init__(self, policy: int, timestamp: int):
        self.policy = policy
        self.timestamp = timestamp
        self.pool_ = []

    def get_pool_hash(self):
        print(type(self.pool))
        return PolicyPoolModel.hash_util(self.pool)

    @staticmethod
    def hash_util(d: dict or list) -> int:
        try:
            assert type(d) == dict or type(d) == list
        except AssertionError:
            print(type(d), file=sys.stderr)
        hashable = json.dumps(d)
        hash_tmp = SHA256Hash().new(hashable.encode())
        return Conversion.OS2IP(hash_tmp.digest())

    @property
    def pool(self) -> list:
        res = list()
        pool = json.loads(self.pool_)
        for x in pool:
            x = json.loads(x)
            data = {
              "hash": PolicyPoolModel.hash_util(x),
              "proofs": x
            }
            res.append(data)
        return res

    @pool.setter
    def pool(self, proofs: dict):
        self.append_to_pool(proofs)

    def append_to_pool(self, proofs: dict):
        tmp = json.loads(str(self.pool_))
        tmp.append(json.dumps(proofs))
        self.pool_ = json.dumps(tmp)
        self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
