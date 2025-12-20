import time
import threading
from queue import Queue

from flask import request, jsonify
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src import db
from src.models.sensor_model import Sensor, SensorSchema
from src.models.signal_model import Signal, SignalSchema


clock_event = threading.Event()
kill_event = threading.Event()

engine = create_engine("sqlite:///../database/database.db")


def create():
    try:
        sensor = Sensor(**request.json)
        db.session.add(sensor)
        db.session.commit()
        sensor_schema = SensorSchema()
        res = {"status": "success", "data": sensor_schema.dump(sensor)}
        return jsonify(res), 202
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def read(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        sensor_schema = SensorSchema()
        res = {"status": "success", "data": sensor_schema.dump(sensor)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def read_all():
    try:
        sensors = Sensor.query.all()
        sensors_schema = SensorSchema(many=True)
        res = {"status": "success", "data": sensors_schema.dump(sensors)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def update(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        sensor_schema = SensorSchema()
        Sensor.query.filter_by(id=sensor_id).update(request.json)
        db.session.commit()
        res = {"status": "success", "data": sensor_schema.dump(sensor)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        db.session.delete(sensor)
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def delete_all():
    try:
        Sensor.query.delete()
        db.session.commit()
        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_signals(sensor_id):
    try:
        signals = Signal.query.filter_by(sensor_id=sensor_id)
        signals_schema = SignalSchema(many=True)
        res = {"status": "success", "data": signals_schema.dump(signals)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def start(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        signals = Signal.query.filter_by(sensor_id=sensor_id).order_by(Signal.id.asc())

        sensor.state = True
        db.session.commit()

        print("Running sensor {}...".format(sensor.id))

        input_queue = Queue()
        output_queue = Queue()

        clock_thread = threading.Thread(
            target=sensor.clock,
            args=(
                clock_event,
                kill_event,
            ),
        )
        clock_thread.start()

        receive_thread = threading.Thread(
            target=sensor.receive,
            args=(
                Signal,
                input_queue,
                clock_event,
            ),
        )
        receive_thread.start()

        process_thread = threading.Thread(
            target=sensor.process,
            args=(Signal, input_queue, output_queue, clock_event),
        )
        process_thread.start()

        transmit_thread = threading.Thread(
            target=sensor.transmit,
            args=(Signal, output_queue, clock_event),
        )
        transmit_thread.start()

        res = {"status": "success", "data": None}
        return jsonify(res), 202
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def stop(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)

        sensor.state = False
        db.session.commit()

        kill_event.set()
        time.sleep(1)
        kill_event.clear()

        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_state(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)

        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "state": sensor.state,
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def set_state(sensor_id, state):
    try:
        sensor = Sensor.query.get(sensor_id)
        sensor.state = state
        db.session.commit()

        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "state": sensor.state,
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def set_values(sensor_id):
    try:
        signals = Signal.query.filter_by(sensor_id=sensor_id)
        signals_schema = SignalSchema(many=True)

        values = request.json["values"]

        for index, signal in enumerate(signals):
            signal.setpoint = values[index]["setpoint"]

        db.session.commit()

        res = {"status": "success", "data": signals_schema.dump(signals)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_data(sensor_id, start_date, end_date):
    try:
        sensor = Sensor.query.get(sensor_id)
        signals = Signal.query.filter_by(sensor_id=sensor_id).order_by(Signal.id.asc())

        x_columns = []
        y_columns = []
        for signal in signals:
            column = "signal_{}".format(signal.id)
            if signal.group == "input":
                x_columns.append(column)
            elif signal.group == "output":
                y_columns.append(column)

        query = """SELECT * FROM data WHERE date_time BETWEEN ? AND ? ORDER BY date_time ASC"""

        start_date = start_date.translate(str.maketrans({"T": " ", "Z": " "}))
        end_date = end_date.translate(str.maketrans({"T": " ", "Z": " "}))

        result = pd.read_sql(
            query,
            con=engine,
            params=(start_date, end_date),
            parse_dates=["date_time"],
            index_col="date_time",
        )

        if not result.empty:
            date_time = (
                pd.to_datetime(result.index.values)
                .strftime("%Y-%m-%d %H:%M:%S")
                .tolist()
            )

            values = []
            for signal in signals:
                column = "signal_{}".format(signal.id)
                values.append(
                    {
                        "id": signal.id,
                        "name": signal.name,
                        "description": signal.description,
                        "value": np.around(
                            result[column].values,
                            decimals=3,
                        ).tolist(),
                    }
                )

                res = {
                    "status": "success",
                    "data": {
                        "date_time": date_time,
                        "values": values,
                    },
                }
        else:
            res = {
                "status": "success",
                "data": None,
            }

        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def get_points(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        signals = Signal.query.filter_by(sensor_id=sensor_id).order_by(Signal.id.asc())

        x_columns = []
        y_columns = []
        for signal in signals:
            column = "signal_{}".format(signal.id)
            if signal.group == "input":
                x_columns.append(column)
            elif signal.group == "output":
                y_columns.append(column)

        query = """SELECT * FROM data ORDER BY date_time DESC LIMIT 1"""
        # query = """SELECT * FROM data ORDER BY date_time ASC"""

        result = pd.read_sql(
            query,
            con=engine,
            parse_dates=["date_time"],
            index_col="date_time",
        )

        if not result.empty:
            # date_time = (
            #     pd.to_datetime(result.index.values)
            #     .strftime("%Y-%m-%d %H:%M:%S")
            #     .tolist()
            # )

            values = []
            for signal in signals:
                column = "signal_{}".format(signal.id)
                values.append(
                    {
                        "id": signal.id,
                        "name": signal.name,
                        "description": signal.description,
                        "date_time": pd.to_datetime(result.index.values)
                        .strftime("%Y-%m-%dT%H:%M:%S")
                        .tolist().pop(),
                        "value": np.around(
                            result[column].values,
                            decimals=3,
                        ).tolist().pop(),
                    }
                )

                res = {
                    "status": "success",
                    "data": values,
                }
        else:
            res = {
                "status": "success",
                "data": None,
            }

        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404
