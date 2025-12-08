import secrets
import datetime
from flask import request, jsonify
from flask_mail import Message
import jwt
from src import db, mail
from src.models.user_model import User, UserSchema
from src.config import SECRET_KEY, EXPIRATION_TIME


def encode_token(id):
    token = jwt.encode(
        {
            "id": id,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=EXPIRATION_TIME),
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except BaseException as err:
        return None


def protect_middleware():
    try:
        header = request.headers["authorization"]
        bearer, _, token = header.partition(" ")
        payload = decode_token(token)
        print(bearer, token, payload)

        if bearer == "Bearer" and payload is not None:
            user = User.query.filter_by(id=payload["id"]).first()
            if user is not None:
                pass
            else:
                res = {
                    "status": "unauthorized",
                    "message": "Please, sign in to get access.",
                }
                return jsonify(res), 401
        else:
            res = {
                "status": "unauthorized",
                "message": "Please, sign in to get access.",
            }
            return jsonify(res), 401
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def protect():
    if request.endpoint not in ["index", "auth_bp.login", "auth_bp.restore_password"]:
        if request.method != "OPTIONS":
            return protect_middleware()


def login():
    try:
        # Get credentials (e-mail and password) in request body
        email, password = request.json["email"], request.json["password"]
        # Select the user with that email
        user = User.query.filter_by(email=email).first()
        user_schema = UserSchema()
        if user is not None:
            # Check if the password is valid
            if not user.check_password(password):
                res = {"status": "fail", "message": "Incorrect email or password."}
                return jsonify(res), 400
            # Generate token with user id
            token = encode_token(user.id)
            # Return generated token and user profile to web app
            res = {
                "status": "success",
                "token": token,
                "data": {
                    "id": user.id,
                    "company_id": user.company_id,
                    "name": user.name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                },
            }
            return jsonify(res), 200
        else:
            res = {"status": "fail", "message": "User not found."}
            return jsonify(res), 404
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def restore_password():
    try:
        email = request.json["email"]
        user = User.query.filter_by(email=email).first()
        user_schema = UserSchema()
        if user is not None:
            password_length = 8
            password = secrets.token_urlsafe(password_length)
            password_encrypted = user.encrypt_password(password)
            user.password = password_encrypted
            db.session.commit()

            msg = Message("SGR Stem - Password restore")
            msg.sender = "contato@sgrautomacao.com"
            msg.recipients = [email]
            msg.body = "Password: {}".format(password)
            mail.send(msg)

            res = {"status": "success"}
            return jsonify(res), 200
        else:
            res = {"status": "fail", "message": "User not found."}
            return jsonify(res), 401
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400
