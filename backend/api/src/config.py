import os

SECRET_KEY = os.urandom(32)
EXPIRATION_TIME = 60 * 60 * 2
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "sqlite:///../../database/database.db",
)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", SQLALCHEMY_DATABASE_URI
)
SQLALCHEMY_TRACK_MODIFICATIONS = False


INFLUXDB_URL = os.environ.get(
    "INFLUXDB_URL",
    "http://localhost:8086",
)
INFLUXDB_TOKEN = os.environ.get(
    "INFLUXDB_TOKEN",
    "e0CmbRWan39mFimiuIKZB6gCCKO-uVfIoL9BfxaSXz9P0k72AEn4kbem8rdUfwWYbLLT61kBscIPQiaCj5pxpA==",
)
INFLUXDB_BUCKET = os.environ.get(
    "INFLUXDB_BUCKET",
    "stem-sensor",
)
