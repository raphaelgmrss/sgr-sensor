from datetime import datetime
import bcrypt
from flask_marshmallow import Marshmallow
from src import db

ma = Marshmallow()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    role = db.Column(db.String, default="admin")
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, last_name, email, password):
        self.name = name
        self.last_name = last_name
        self.email = email
        self.password = self.encrypt_password(password)

        self.encrypt_password(password)

    def encrypt_password(self, password):
        password = bytes(password, encoding="utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        password = hashed.decode("ascii")
        return password

    def check_password(self, password):
        if bcrypt.checkpw(
            bytes(password, encoding="utf-8"), bytes(self.password, encoding="utf-8")
        ):
            return True
        else:
            return False


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()
    role = ma.auto_field()
    created_date = ma.auto_field()
