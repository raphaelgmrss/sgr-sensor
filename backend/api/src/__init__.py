from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from sqlalchemy import create_engine

import src.config as config

app = Flask(__name__)
app.config.from_object("src.config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
cors = CORS(app)
mail = Mail(app)

engine = {
    "api": create_engine(config.SQLALCHEMY_DATABASE_URI),
}

from src.routes.auth_routes import auth_bp
from src.routes.user_routes import user_bp
from src.routes.sensor_routes import sensor_bp
from src.routes.signal_routes import signal_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(sensor_bp)
app.register_blueprint(signal_bp)
