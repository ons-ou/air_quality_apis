from sqlalchemy import ForeignKey

from config import db


class County(db.Model):
    __tablename__ = 'counties'
    state_code = db.Column(db.String(2), ForeignKey('states.state_code'), primary_key=True)
    county_code = db.Column(db.String(3), primary_key=True)
    county_name = db.Column(db.String(255))
    state = db.relationship("State", backref="counties")
