from sqlalchemy.orm import relationship

from cp.models import KeyModel
from cp import db
from cp.models.PolicyPoolModel import PolicyPoolModel


class PolicyModel(db.Model):
    __tablename__ = 'policies'

    policy = db.Column(db.Integer, primary_key=True)
    publication_interval = db.Column(db.Integer)
    lifetime = db.Column(db.Integer)
    description = db.Column(db.String)
    keys = relationship("KeyModel")
    pools = relationship("PolicyPoolModel")

    def __init__(self, publication_interval, lifetime, description):
        self.publication_interval = publication_interval
        self.lifetime = lifetime
        self.description = description if description is not None else "No description given"

    def __repr__(self):
        return "<Policy(policy='%s', description='%s')>" % (self.policy, self.description)

    def __str__(self):
        return "Policy(policy='%s', description='%s')" % (self.policy, self.description)

    def get_key(self, timestamp: int) -> KeyModel:
        """
            Find a policy key model based on the timestamp given.
            :param timestamp: (int)
            :return: (KeyModel) or None
        """
        return self.__get_from_list(self.keys, timestamp)

    def get_pool(self, timestamp: int) -> PolicyPoolModel:
        pool = self.__get_from_list(self.pools, timestamp)
        if pool is None:
            pool = PolicyPoolModel(self.policy, timestamp)
            pool.save_to_db()
            self.save_to_db()
        return pool

    @staticmethod
    def __get_from_list(ls, timestamp) -> db.Model:
        for x in ls:
            if x.timestamp == timestamp:
                return x
        return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
