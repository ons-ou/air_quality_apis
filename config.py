import os

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '00000')
DB_NAME = os.getenv('DB_NAME', 'air_quality')


DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

#  IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = DB_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = True

DEBUG = True

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
CORS(app)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
