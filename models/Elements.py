from config import db
from models.AbstractModel import AbstractModel


class PollutantData(AbstractModel, db.Model):
    __abstract__ = True
    first_max_value = db.Column(db.Numeric)
    first_max_hour = db.Column(db.Numeric)
    arithmetic_mean = db.Column(db.Numeric)


class CO(PollutantData):
    __tablename__ = 'co_data'


class NO2(PollutantData):
    __tablename__ = 'no2_data'


class Ozone(PollutantData):
    __tablename__ = 'ozone_data'


class PM10(PollutantData):
    __tablename__ = 'pm10_data'


class PM25(PollutantData):
    __tablename__ = 'pm2_5_data'


class SO2(PollutantData):
    __tablename__ = 'so2_data'
