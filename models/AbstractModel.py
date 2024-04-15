from sqlalchemy import ForeignKeyConstraint, ForeignKey, Column, Numeric, Integer, String, Date
from sqlalchemy.orm import declarative_base, declared_attr, relationship

from config import db

Base = declarative_base()


class AbstractModel(Base):
    __abstract__ = True
    date_local = Column(Date, primary_key=True)
    longitude = Column(Numeric, primary_key=True)
    latitude = Column(Numeric, primary_key=True)
    observation_count = Column(Integer)
    state_code = Column(String(2), ForeignKey('counties.state_code'))
    county_code = Column(String(3), ForeignKey('counties.county_code'))
    season = Column(String(255))
    day_of_week = Column(Integer)
