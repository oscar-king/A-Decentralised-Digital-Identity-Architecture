# SessionModel.py

from user import db


class SessionModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(), unique=True)
    refresh_token = db.Column(db.String(), unique=True)

    @property
    def get_access_token(self):
        return self.access_token

    @property
    def get_refresh_token(self):
        return self.refresh_token

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def delete():
        db.session.query(SessionModel).delete()
        db.session.commit()
