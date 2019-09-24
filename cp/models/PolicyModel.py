from sqlalchemy.orm import relationship

from cp import db
from cp.models.KeyModel import KeyModel


class PolicyModel(db.Model):
    __tablename__ = 'policies'

    policy = db.Column(db.Integer, primary_key=True)
    publication_interval = db.Column(db.Integer)
    lifetime = db.Column(db.Integer)
    description = db.Column(db.String)
    keys = relationship("KeyModel")

    def __init__(self, publication_interval, lifetime, description):
        self.publication_interval = publication_interval
        self.lifetime = lifetime
        self.description = description if description is not None else "No description given"

    def __repr__(self):
        return "<Policy(policy='%s', description='%s')>" % (self.policy, self.description)

    def __str__(self):
        return "Policy(policy='%s', description='%s')" % (self.policy, self.description)

    def get_key(self, timestamp):
        # return KeyModel.query.join(PolicyModel).filter(KeyModel.policy == self.policy).all()
        for x in self.keys:
            if x.timestamp == timestamp:
                return x
        return None

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
