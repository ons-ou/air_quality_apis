from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from config import db
from models.AbstractModel import AbstractModel


class AQI(AbstractModel, db.Model):
    __tablename__ = 'aqi_data'
    aqi = db.Column(db.Numeric)


