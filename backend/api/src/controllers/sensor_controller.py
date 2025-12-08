import time
import threading
from queue import Queue

from flask import request, jsonify
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from src import db, engine, config
from src.models.sensor_model import Sensor, SensorSchema
from src.models.signal_model import Signal, SignalSchema
from src.utils import (
    torch,
    Repeater,
    Generator,
    Evaluator,
    MinMaxScaler,
    device,
)


clock_event = threading.Event()
kill_event = threading.Event()


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
        junctions = (
            Junction.query.filter_by(sensor_id=sensor_id)
            .order_by(Junction.id.asc())
            .all()
        )
        signals_ids = []
        for junction in junctions:
            signals_ids.append(junction.signal_id)
        signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
            Signal.id.asc()
        )
        signals_schema = SignalSchema(many=True)
        res = {"status": "success", "data": signals_schema.dump(signals)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def get_builds(sensor_id):
    try:
        builds = Build.query.filter_by(sensor_id=sensor_id)
        builds_schema = BuildSchema(many=True)
        res = {"status": "success", "data": builds_schema.dump(builds)}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 404


def build(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        junctions = (
            Junction.query.filter_by(sensor_id=sensor_id)
            .order_by(Junction.id.asc())
            .all()
        )
        signals_ids = []
        for junction in junctions:
            signals_ids.append(junction.signal_id)
        signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
            Signal.id.asc()
        )

        # Data
        r.hset("sensor_{}".format(sensor_id), key="state", value=0)
        r.hset("sensor_{}".format(sensor_id), key="mode", value=0)

        table = "sensor_build_{}".format(sensor_id)
        query = "SELECT * FROM {} ORDER BY date_time ASC;".format(table)
        df = pd.read_sql(query, engine["build"]).set_index("date_time")
        df.index = pd.to_datetime(df.index)
        df.sort_index(ascending=True, inplace=True)

        x_columns = []
        y_columns = []
        readings = {}
        for signal in signals:
            column = signal.name
            if signal.group == "input":
                readings[column] = signal.initial_value
                x_columns.append(column)
            elif signal.group == "output":
                y_columns.append(column)

        x = df[x_columns]
        y = df[y_columns]
        r.mset(readings)

        generator = Generator()
        train_dataloader, val_dataloader = generator.generate_dataloaders(
            x.to_numpy(), y.to_numpy(), sensor.lag, sensor.batch_size
        )

        # Sensor
        config = {
            "input_size": sensor.input_size + sensor.output_size,
            "output_size": sensor.output_size,
            "hidden_size": sensor.hidden_size,
            "num_layers": sensor.num_layers,
            "learning_rate": sensor.learning_rate,
            "dropout": sensor.dropout,
            "lag": sensor.lag,
            "epochs": sensor.epochs,
        }

        repeater = Repeater(**config).to(device)

        # Train
        start = time.time()
        repeater.fit(train_dataloader, val_dataloader)
        end = time.time()
        elapsed_time = end - start
        torch.save(repeater.state_dict(), sensor.model)

        # Test
        for parameter in repeater.parameters():
            parameter.requires_grad = False
        repeater.eval()

        x_test = generator.x_test
        x_val = generator.x_val
        y_val = generator.y_val
        y_test_scaled = repeater.test(x_test, (x_val, y_val))
        y_test = generator.y_scaler.inverse_transform(y_test_scaled)

        # Evaluate
        evaluator = Evaluator()
        metrics_dict = evaluator.measure(generator.y_test, y_test)

        build_data = {
            "company_id": sensor.company_id,
            "sensor_id": sensor.id,
            "elapsed_time": elapsed_time,
            "train_loss": repeater.train_loss,
            "val_loss": repeater.val_loss,
            "explained_variance_score": metrics_dict["explained_variance_score"],
            "mean_absolute_error": metrics_dict["mean_absolute_error"],
            "mean_squared_error": metrics_dict["mean_squared_error"],
            "root_mean_squared_error": metrics_dict["root_mean_squared_error"],
            "median_absolute_error": metrics_dict["median_absolute_error"],
            "mean_absolute_percentage_error": metrics_dict[
                "mean_absolute_percentage_error"
            ],
            "d2_absolute_error_score": metrics_dict["d2_absolute_error_score"],
            "d2_pinball_score": metrics_dict["d2_pinball_score"],
            "r2_score": metrics_dict["r2_score"],
            "x_scaler_min": generator.x_scaler.min_,
            "x_scaler_scale": generator.x_scaler.scale_,
            "x_scaler_data_min": generator.x_scaler.data_min_,
            "x_scaler_data_max": generator.x_scaler.data_max_,
            "x_scaler_data_range": generator.x_scaler.data_range_,
            "x_scaler_n_features_in": generator.x_scaler.n_features_in_,
            "x_scaler_n_samples_seen": generator.x_scaler.n_samples_seen_,
            "y_scaler_min": generator.y_scaler.min_,
            "y_scaler_scale": generator.y_scaler.scale_,
            "y_scaler_data_min": generator.y_scaler.data_min_,
            "y_scaler_data_max": generator.y_scaler.data_max_,
            "y_scaler_data_range": generator.y_scaler.data_range_,
            "y_scaler_n_features_in": generator.y_scaler.n_features_in_,
            "y_scaler_n_samples_seen": generator.y_scaler.n_samples_seen_,
        }
        build = Build(**build_data)
        build_schema = SignalSchema()
        db.session.add(build)
        db.session.commit()

        res = {"status": "success", "data": build_schema.dump(build)}
        return jsonify(res), 202
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def start(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        junctions = (
            Junction.query.filter_by(sensor_id=sensor_id)
            .order_by(Junction.id.asc())
            .all()
        )
        signals_ids = []
        for junction in junctions:
            signals_ids.append(junction.signal_id)
        signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
            Signal.id.asc()
        )
        build = (
            Build.query.filter_by(sensor_id=sensor.id).order_by(Build.id.desc()).first()
        )
        company = (
            Company.query.filter_by(id=sensor.company_id)
            .order_by(Company.id.desc())
            .first()
        )

        print("Running sensor {}...".format(sensor.id))
        r.hset("sensor_{}".format(sensor_id), key="state", value=1)

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
                signals,
                input_queue,
                clock_event,
            ),
        )
        receive_thread.start()

        run_thread = threading.Thread(
            target=sensor.run,
            args=(
                build,
                signals,
                input_queue,
                output_queue,
            ),
        )
        run_thread.start()

        transmit_thread = threading.Thread(
            target=sensor.transmit,
            args=(
                signals,
                output_queue,
                company.name,
            ),
        )
        transmit_thread.start()

        if r.hget("sensor_{}".format(sensor_id), "mode") == b"1":
            generate_thread = threading.Thread(
                target=sensor.generate,
                args=(
                    signals,
                    clock_event,
                ),
            )
            generate_thread.start()

        res = {"status": "success", "data": None}
        return jsonify(res), 202
    except Exception as err:
        res = {"status": "fail", "message": repr(err)}
        return jsonify(res), 400


def stop(sensor_id):
    try:
        r.hset("sensor_{}".format(sensor_id), key="state", value=0)

        kill_event.set()
        time.sleep(1)
        kill_event.clear()

        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def reset():
    try:
        sensors = Sensor.query.all()

        for sensor in sensors:
            r.hset("sensor_{}".format(sensor.id), key="state", value=0)

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
        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "state": int(r.hget("sensor_{}".format(sensor_id), "state")),
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def set_state(sensor_id, state):
    try:
        r.hset("sensor_{}".format(sensor_id), key="state", value=state)

        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "state": int(r.hget("sensor_{}".format(sensor_id), "state")),
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_states():
    try:
        sensors = Sensor.query.all()

        states = []
        for sensor in sensors:
            states.append(
                {
                    "sensor_id": sensor.id,
                    "state": int(r.hget("sensor_{}".format(sensor.id), "state")),
                }
            )

        res = {"status": "success", "data": states}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_mode(sensor_id):
    try:
        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "mode": int(r.hget("sensor_{}".format(sensor_id), "mode")),
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def set_mode(sensor_id, mode):
    try:
        sensor = Sensor.query.get(sensor_id)
        junctions = (
            Junction.query.filter_by(sensor_id=sensor_id)
            .order_by(Junction.id.asc())
            .all()
        )
        signals_ids = []
        for junction in junctions:
            signals_ids.append(junction.signal_id)
        signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
            Signal.id.asc()
        )

        mode_past = r.hget("sensor_{}".format(sensor_id), "mode")
        r.hset("sensor_{}".format(sensor_id), key="mode", value=mode)

        if mode == 1 and mode_past == b"0":
            generate_thread = threading.Thread(
                target=sensor.generate,
                args=(
                    signals,
                    clock_event,
                ),
            )
            generate_thread.start()

        res = {
            "status": "success",
            "data": {
                "sensor_id": sensor_id,
                "mode": int(r.hget("sensor_{}".format(sensor_id), "mode")),
            },
        }
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500


def get_data(sensor_id, start_date, end_date):
    try:
        sensor = Sensor.query.get(sensor_id)
        junctions = (
            Junction.query.filter_by(sensor_id=sensor_id)
            .order_by(Junction.id.asc())
            .all()
        )
        signals_ids = []
        for junction in junctions:
            signals_ids.append(junction.signal_id)
        signals = Signal.query.filter(Signal.id.in_(signals_ids)).order_by(
            Signal.id.asc()
        )
        company = (
            Company.query.filter_by(id=sensor.company_id)
            .order_by(Company.id.desc())
            .first()
        )

        custom = request.args.get("custom")
        points = int(request.args.get("points"))

        if custom == None:
            custom = False
        elif custom == "true":
            custom = True
        elif custom == "false":
            custom = False

        norm = request.args.get("normalization")
        if norm == None:
            norm = False
        elif norm == "true":
            norm = True
        elif norm == "false":
            norm = False

        x_columns = []
        y_columns = []
        for signal in signals:
            column = signal.description
            if signal.group == "input":
                x_columns.append(column)
            elif signal.group == "output":
                y_columns.append(column)

        columns = ["_time"] + x_columns + y_columns

        client = InfluxDBClient(
            url=config.INFLUXDB_URL,
            token=config.INFLUXDB_TOKEN,
            org=company.name,
        )
        query_api = client.query_api()

        if custom:
            query = 'from(bucket: "{}") |> range(start: {}, stop: {}) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
                config.INFLUXDB_BUCKET,
                start_date,
                end_date,
                sensor.description,
            )
        else:
            # query = 'from(bucket: "{}") |> range(start: 0) |> tail(n: {}) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
            #     config.INFLUXDB_BUCKET,
            #     points,
            #     sensor.description,
            # )
            query = 'from(bucket: "{}") |> range(start: -{}m) |> filter(fn: (r) => r["_measurement"] == "{}") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'.format(
                config.INFLUXDB_BUCKET,
                points,
                sensor.description,
            )

        result = query_api.query_data_frame(query)

        if not result.empty:
            result = result[columns].set_index("_time")
            result.index.name = "date_time"
            # result.resample("{}s".format(sensor.sampling_period)).interpolate(
            #     method="linear", limit_direction="both", axis=0, inplace=True
            # )
            date_time = (
                pd.to_datetime(result.index.values)
                .strftime("%Y-%m-%d %H:%M:%S")
                .tolist()
            )

            if norm:
                scaler = MinMaxScaler(feature_range=(0, 1))
                result_scaled = scaler.fit_transform(result)
                result[result.columns[:]] = result_scaled

            values = []
            for signal in signals:
                column = signal.description
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
        res = {"status": "fail", "message": (err)}
        return jsonify(res), 404


def set_variables():
    try:
        r.mset(request.json)

        res = {"status": "success", "data": None}
        return jsonify(res), 200
    except Exception as err:
        res = {"status": "error", "message": repr(err)}
        return jsonify(res), 500
