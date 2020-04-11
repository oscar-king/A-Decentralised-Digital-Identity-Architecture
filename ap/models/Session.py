import json
import sys

from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from charm.toolbox.conversion import Conversion
from ap import db
from ap.utils.ledger_utils import get_cp_pubkey
from crypto_utils.conversions import SigConversion
from crypto_utils.signatures import BlindSignatureVerifier


class Session(db.Model):
    y = db.Column(db.String(256), primary_key=True)
    pubk_ = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.Integer)
    policy = db.Column(db.Integer)
    u_ = db.Column(db.String)
    d_ = db.Column(db.String)
    s1_ = db.Column(db.String)
    s2_ = db.Column(db.String)

    def __init__(self, y: str, pubk: int):
        self.y = y
        self.pubk_ = str(pubk)
        self.timestamp = None
        self.policy = None
        self.u_ = None
        self.d_ = None
        self.s1_ = None
        self.s2_ = None

    @property
    def pubk(self) -> bytes:
        return Conversion.IP2OS(int(self.pubk_))

    @property
    def u(self):
        return SigConversion.strlist2modint(self.u_)

    @u.setter
    def u(self, u):
        self.u_ = SigConversion.modint2strlist(u)

    @property
    def d(self):
        return SigConversion.strlist2modint(self.d_)

    @d.setter
    def d(self, d):
        self.d_ = SigConversion.modint2strlist(d)

    @property
    def s1(self):
        return SigConversion.strlist2modint(self.s1_)

    @s1.setter
    def s1(self, s1):
        self.s1_ = SigConversion.modint2strlist(s1)

    @property
    def s2(self):
        return SigConversion.strlist2modint(self.s2_)

    @s2.setter
    def s2(self, s2):
        self.s2_ = SigConversion.modint2strlist(s2)

    @property
    def get_timestamp(self):
        return self.timestamp

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def check(self, signature: int):
        # Convert back to bytes
        sig = Conversion.IP2OS(signature)

        # Verifier setup
        ecc = ECC.import_key(self.pubk)
        verifier = DSS.new(ecc, 'fips-186-3')
        new_hash = SHA256.new(bytes.fromhex(self.y))

        # We need to verify the signature on the hash. The verifier throws an exception if it doesn't verify.
        try:
            verifier.verify(new_hash, sig)
            return True
        except Exception as e:
            print(str(e), file=sys.stderr)
            return False

    def verify_blind(self, cp, blind_signature):
        # Convert to modular integer dictionary
        sig = SigConversion.convert_dict_modint(json.loads(blind_signature))
        cp_pubk = get_cp_pubkey(cp, self.timestamp, self.policy)
        if cp_pubk is None:
            return False
        else:
            verifier = BlindSignatureVerifier(cp_pubk)
            message = Conversion.OS2IP(self.pubk)
            return verifier.verify(sig, message)

    @staticmethod
    def find(y: str):
        tmp = Session.query.get(y)
        if tmp:
            return tmp
        else:
            return None
