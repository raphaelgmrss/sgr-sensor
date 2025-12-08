from flask import request, jsonify
from src import db
from src.models.user_model import User, UserSchema


def create():
    try:
        user = User(**request.json)
        db.session.add(user)
        db.session.commit()
        user_schema = UserSchema()
        res = {"status": "success", "data": user_schema.dump(user)}
        return jsonify(res), 201
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def read(user_id):
    try:
        user = User.query.get(user_id)
        user_schema = UserSchema()
        res = {"status": "success", "data": user_schema.dump(user)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def read_all():
    try:
        users = User.query.all()
        users_schema = UserSchema(many=True)
        res = {"status": "success", "data": users_schema.dump(users)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def update(user_id):
    try:
        user = User.query.get(user_id)
        user_schema = UserSchema()
        password = request.json["password"]
        request.json["password"] = user.encrypt_password(password)
        User.query.filter_by(id=user_id).update(request.json)
        db.session.commit()
        res = {"status": "success", "data": user_schema.dump(user)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete(user_id):
    try:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete_all():
    try:
        User.query.delete()
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500
