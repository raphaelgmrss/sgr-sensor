import time
import threading
from queue import Queue

from flask import request, jsonify
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient

from src import db, config
from src.models.sensor_model import Sensor, SensorSchema
from src.models.signal_model import Signal, SignalSchema


clock_event = threading.Event()
kill_event = threading.Event()

from datetime import datetime


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


# def get_data(sensor_id, start_date, end_date):
#     try:
#         sensor = Sensor.query.get(sensor_id)
#         junctions = (
#             Junction.query.filter_by(sensor_id=sensor_id)
#             .order_by(Junction.id.asc())
#             .all()
#         )
#         signals_ids = []
#         for junction in junctions:
#             signals_ids.append(junction.signal_id)
#         signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
#             Signal.id.asc()
#         )
#         company = (
#             Company.query.filter_by(id=sensor.company_id)
#             .order_by(Company.id.desc())
#             .first()
#         )

#         custom = request.args.get("custom")
#         points = int(request.args.get("points"))

#         if custom == None:
#             custom = False
#         elif custom == "true":
#             custom = True
#         elif custom == "false":
#             custom = False

#         norm = request.args.get("normalization")
#         if norm == None:
#             norm = False
#         elif norm == "true":
#             norm = True
#         elif norm == "false":
#             norm = False

#         x_columns = []
#         y_columns = []
#         for signal in signals:
#             column = signal.description
#             if signal.group == "input":
#                 x_columns.append(column)
#             elif signal.group == "output":
#                 y_columns.append(column)

#         columns = ["_time"] + x_columns + y_columns

#         client = InfluxDBClient(
#             url=config.INFLUXDB_URL,
#             token=config.INFLUXDB_TOKEN,
#             org=company.name,
#         )
#         query_api = client.query_api()

#         if custom:
#             query = 'from(bucket: "{}") |> range(start: {}, stop: {}) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
#                 config.INFLUXDB_BUCKET,
#                 start_date,
#                 end_date,
#                 sensor.description,
#             )
#         else:
#             # query = 'from(bucket: "{}") |> range(start: 0) |> tail(n: {}) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
#             #     config.INFLUXDB_BUCKET,
#             #     points,
#             #     sensor.description,
#             # )
#             query = 'from(bucket: "{}") |> range(start: -{}m) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
#                 config.INFLUXDB_BUCKET,
#                 points,
#                 sensor.description,
#             )

#         result = query_api.query_data_frame(query)

#         if not result.empty:
#             result = result[columns].set_index("_time")
#             result.index.name = "date_time"
#             # result.resample("{}s".format(sensor.sampling_period)).interpolate(
#             #     method="linear", limit_direction="both", axis=0, inplace=True
#             # )
#             date_time = (
#                 pd.to_datetime(result.index.values)
#                 .strftime("%Y-%m-%d %H:%M:%S")
#                 .tolist()
#             )

#             if norm:
#                 scaler = MinMaxScaler(feature_range=(0, 1))
#                 result_scaled = scaler.fit_transform(result)
#                 result[result.columns[:]] = result_scaled

#             values = []
#             for signal in signals:
#                 column = signal.description
#                 values.append(
#                     {
#                         "id": signal.id,
#                         "name": signal.name,
#                         "description": signal.description,
#                         "value": np.around(
#                             result[column].values,
#                             decimals=3,
#                         ).tolist(),
#                     }
#                 )

#                 res = {
#                     "status": "success",
#                     "data": {
#                         "date_time": date_time,
#                         "values": values,
#                     },
#                 }
#         else:
#             res = {
#                 "status": "success",
#                 "data": None,
#             }

#         return jsonify(res), 200
#     except Exception as err:
#         res = {"status": "fail", "message": (err)}
#         return jsonify(res), 404


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
