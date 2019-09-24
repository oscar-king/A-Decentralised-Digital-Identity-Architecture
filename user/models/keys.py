# keys.py
from crypto_utils.signatures import UserBlindSignature
from user import db
from Crypto.PublicKey import ECC


class KeyModel(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    cp_ = db.Column(db.String(50))
    policy_ = db.Column(db.Integer)
    key_pair_ = db.Column(db.LargeBinary)
    user_blind_sig_ = db.Column(db.String)
    interval_timestamp_ = db.Column(db.Integer)
    proof_hash_ = db.Column(db.String)

    def __init__(self, cp="CP", policy=1, signer=None, interval=None):
        self.cp_ = cp
        self.policy_ = policy
        self.key_pair_ = ECC.generate(curve='P-256').export_key(format='DER')
        self.user_blind_sig_ = signer.encode() if signer is not None else None
        self.interval_timestamp_ = interval

    @property
    def id(self):
        return self.id_

    @property
    def signer(self):
        return UserBlindSignature().decode(self.user_blind_sig_)

    @signer.setter
    def signer(self, signer):
        self.user_blind_sig_ = signer

    @property
    def cp(self):
        """
        :return: cp: String
        """
        return self.cp_

    @property
    def key_pair(self):
        """
        :return: ECC object
        """
        return ECC.import_key(encoded=self.key_pair_)

    @property
    def public_key(self):
        """
        Returns a DER encoded copy of the public key stored
        :return: (bytes)
        """
        key = self.key_pair
        return key.public_key().export_key(format='DER')

    @property
    def interval_timestamp(self):
        """
        :return: POSIX timestamp: int
        """
        return self.interval_timestamp_

    @property
    def policy(self):
        return self.policy_

    @property
    def proof_hash(self):
        return self.proof_hash_

    @proof_hash.setter
    def proof_hash(self, hs):
        self.proof_hash_ = hs

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        pass