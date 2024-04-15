from config import db


class State(db.Model):
    __tablename__ = "states"
    state_code = db.Column(db.String(2), primary_key=True)
    state_name = db.Column(db.String(255))