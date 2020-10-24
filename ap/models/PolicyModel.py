from charm.toolbox.integergroup import IntegerGroupQ
from sqlalchemy.orm import relationship

from ap import db
from ap.models.KeyModel import KeyModel
from crypto_utils.signatures import SignerBlindSignature


class PolicyModel(db.Model):
    __tablename__ = 'policies'

    policy = db.Column(db.Integer, primary_key=True)
    max_age = db.Column(db.Integer)
    description = db.Column(db.String())
    keys = relationship("KeyModel")

    def __init__(self, max_age, description):
        self.max_age = max_age
        self.description = description

    @staticmethod
    def __get_from_list(ls, timestamp) -> db.Model:
        for x in ls:
            if x.timestamp == timestamp:
                return x
        return None

    def get_key(self, timestamp: int) -> KeyModel:
        """
            Find a policy key model based on the timestamp given.
            :param timestamp: (int)
            :return: (KeyModel) or None
        """
        key = self.__get_from_list(self.keys, timestamp)
        if key is None:
            signer = SignerBlindSignature(IntegerGroupQ())
            key = KeyModel(timestamp, self.policy, signer)
            key.save_to_db()
            self.keys.append(key)
            self.save_to_db()
        return key

    @staticmethod
    def find(policy: int):
        tmp = PolicyModel.query.get(policy)
        if tmp:
            return tmp
        else:
            return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
