from flask import request, jsonify
from src import db
from src.models.signal_model import Signal, SignalSchema


def create():
    try:
        signal_data = request.json
        signal = Signal(**signal_data)
        db.session.add(signal)
        db.session.commit()
        signal_schema = SignalSchema()
        res = {"status": "success", "data": signal_schema.dump(signal)}
        return jsonify(res), 202
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def read(signal_id):
    try:
        signal = Signal.query.get(signal_id)
        signal_schema = SignalSchema()
        res = {"status": "success", "data": signal_schema.dump(signal)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def read_all():
    try:
        signals = Signal.query.all()
        signals_schema = SignalSchema(many=True)
        res = {"status": "success", "data": signals_schema.dump(signals)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def update(signal_id):
    try:
        signal = Signal.query.get(signal_id)
        signal_schema = SignalSchema()
        Signal.query.filter_by(id=signal_id).update(request.json)
        db.session.commit()
        res = {"status": "success", "data": signal_schema.dump(signal)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete(signal_id):
    try:
        signal = Signal.query.get(signal_id)
        db.session.delete(signal)
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete_all():
    try:
        Signal.query.delete()
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500
