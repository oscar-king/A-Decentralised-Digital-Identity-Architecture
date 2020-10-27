# keys.py
from datetime import datetime
from typing import Tuple

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion
from sqlalchemy import JSON

from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import UserBlindSignature
from user import db


class KeyModel(db.Model):
    # id_ = db.Column(db.Integer, primary_key=True)
    p_id_ = db.Column(db.Integer, primary_key=True)
    policy_ = db.Column(db.Integer, primary_key=True)
    interval_timestamp_ = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String, primary_key=True)
    provider_type_ = db.Column(db.Integer)
    key_pair_ = db.Column(db.LargeBinary)
    user_blind_sig_ = db.Column(db.String)
    proof_hash_ = db.Column(db.String())
    proof_ = db.Column(JSON)

    def __init__(self, provider_type: str, p_id: int, policy: int = 1, signer: UserBlindSignature = None,
                 interval: int = None, index: str = "1"):
        check = KeyModel.query.filter_by(provider_type_=1 if provider_type == "CP" else 2, p_id_=p_id, policy_=policy,
                                         interval_timestamp_=interval, index=index)
        if check.first() is not None:
            raise Exception("KeyModel already exists")
        else:
            self.type = provider_type
            self.p_id_ = p_id
            self.policy_ = policy
            self.key_pair_ = ECC.generate(curve='P-256').export_key(format='DER')
            self.user_blind_sig_ = signer.encode() if signer is not None else None
            self.interval_timestamp_ = interval
            self.index = index

    def __repr__(self):
        time = datetime.utcfromtimestamp(self.interval_timestamp)
        return "Key[type='%s' timestamp='%s', policy='%s']" % (self.type, time.strftime('%d-%m-%Y %H:%M'), self.policy)

    # @property
    # def id(self) -> int:
    #     return self.id_

    @property
    def signer(self) -> UserBlindSignature:
        return UserBlindSignature().decode(self.user_blind_sig_)

    @signer.setter
    def signer(self, signer) -> None:
        self.user_blind_sig_ = signer.encode() if signer is not None else None

    @property
    def type(self) -> str:
        if self.provider_type_ == 1:
            return 'CP'
        elif self.provider_type_ == 2:
            return 'AP'
        else:
            raise ValueError("Unexpected value for provider_type in user.KeyModel")

    @type.setter
    def type(self, p_type: str):
        if p_type == 'CP':
            self.provider_type_ = 1
        elif p_type == 'AP':
            self.provider_type_ = 2
        else:
            raise Exception('Invalid provider_type assignment in user.KeyModel')

    @property
    def p_id(self) -> int:
        """
        :return: provider_type_id: String
        """
        return self.p_id_

    @property
    def key_pair(self) -> ECC:
        """
        :return: ECC object
        """
        return ECC.import_key(encoded=self.key_pair_)

    @property
    def public_key(self) -> bytes:
        """
        Returns a DER encoded copy of the public key stored
        :return: (bytes)
        """
        key = self.key_pair
        return key.public_key().export_key(format='DER')

    @property
    def interval_timestamp(self) -> int:
        """
        :return: POSIX timestamp: int
        """
        return self.interval_timestamp_

    @property
    def policy(self) -> int:
        return self.policy_

    @property
    def proof_hash(self) -> int:
        return int(self.proof_hash_)

    @proof_hash.setter
    def proof_hash(self, hs: int or str) -> None:
        self.proof_hash_ = str(hs)

    @property
    def proof(self):
        res = dict()
        for key in self.proof_.keys():
            res[key] = SigConversion.strlist2modint(self.proof_[key])
        return res

    @proof.setter
    def proof(self, proof):
        self.proof_ = proof

    def sign(self, y:str) -> Tuple[int, int]:
        key = self.key_pair
        msg_hash = SHA256.new(bytes.fromhex(y))
        signer = DSS.new(key, 'fips-186-3')
        signature = signer.sign(msg_hash)
        return Conversion.OS2IP(msg_hash.digest()), Conversion.OS2IP(signature)

    def generate_blind_signature(self, proof=None):
        if proof is not None:
            signer = self.signer
            proof = SigConversion.convert_dict_modint(proof)
            return signer.gen_signature(proof)
        else:
            if self.proof is None:
                raise Exception("Did not provide a proof nor is one set in the keymodel!")
            else:
                return self.signer.gen_signature(self.proof)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def find(p_id: int, policy: int, timestamp: int, index="1"):
        tmp = KeyModel.query.get((p_id, policy, timestamp, index))
        if tmp:
            return tmp
        else:
            return None