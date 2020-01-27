from sqlalchemy import ForeignKey

from ap import db
from crypto_utils.signatures import SignerBlindSignature


class KeyModel(db.Model):
    timestamp = db.Column(db.Integer, primary_key=True)
    policy = db.Column(db.Integer, ForeignKey('policies.policy'), primary_key=True)
    signer_ = db.Column(db.String)

    def __init__(self, timestamp, policy, signer):
        self.timestamp = timestamp
        self.policy = policy
        self.signer_ = signer.encode()

    def __repr__(self):
        return "<Key(timestamp='%s', policy='%s', pub_key='%s')>" % (self.timestamp, self.policy, self.pub_key)

    @property
    def signer(self):
        return SignerBlindSignature().decode(self.signer_)

    @property
    def get_timestamp(self):
        return self.timestamp

    @property
    def get_policy(self):
        return self.policy

    def get_public_key(self):
        signer = self.signer
        return signer.get_public_key()

    def get_private_key(self):
        sig = self.signer
        return sig.get_private_key()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

