import uuid
from datetime import datetime
import time

from flask_marshmallow import Marshmallow
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import torch
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from src import app, db, text, config


ma = Marshmallow()


class Sensor(db.Model):
    __tablename__ = "sensor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    sampling_period = db.Column(db.Integer, default=1)
    input_size = db.Column(db.Integer)
    output_size = db.Column(db.Integer)
    model_path = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.now)
    # signals = db.relationship(
    #     "Signal", backref="sensor", lazy=True, cascade="all,delete"
    # )

    def __init__(
        self, name, description, sampling_period, input_size, output_size, model_path
    ):
        self.name = name
        self.description = description
        self.sampling_period = sampling_period
        self.input_size = input_size
        self.output_size = output_size
        self.model_path = "../../../database/{}".format(model_path)

    def clock(self, clock_event, kill_event):
        while True:
            clock_event.set()
            clock_event.clear()
            time.sleep(self.sampling_period)

            if kill_event.is_set():
                clock_event.set()
                clock_event.clear()
                break

    def receive(self, input_queue, clock_event):
        while True:
            clock_event.wait()

            with app.app_context():
                signals = (
                    db.session.execute(
                        text("SELECT * FROM signal where id={}".format(self.id))
                    )
                    .mappings()
                    .all()
                )

                x = {"timestamp": datetime.now().isoformat(), "values": []}
                for signal in signals:
                    x["values"].append(signal.setpoint)

            input_queue.put(x)

    def process(self, signals, input_queue, output_queue):
        with app.app_context():
            build = self.builds[-1]
            columns, x_columns, _ = self.get_fields(signals)

        config = {
            "input_size": self.input_size + self.output_size,
            "output_size": self.output_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "learning_rate": self.learning_rate,
            "dropout": self.dropout,
            "lag": self.lag,
            "epochs": self.epochs,
        }

        repeater = Repeater(**config).to(device)

        repeater.load_state_dict(
            torch.load(self.model, map_location=torch.device(device))
        )
        repeater.eval()

        feature_range = (-1, 1)

        x_scaler = MinMaxScaler(feature_range=feature_range)
        x_scaler.min_ = build.x_scaler_min
        x_scaler.scale_ = build.x_scaler_scale
        x_scaler.data_min_ = build.x_scaler_data_min
        x_scaler.data_max_ = build.x_scaler_data_max
        x_scaler.data_range_ = build.x_scaler_data_range
        x_scaler.n_features_in_ = build.x_scaler_n_features_in
        x_scaler.n_samples_seen_ = build.x_scaler_n_samples_seen

        y_scaler = MinMaxScaler(feature_range=feature_range)
        y_scaler.min_ = build.y_scaler_min
        y_scaler.scale_ = build.y_scaler_scale
        y_scaler.data_min_ = build.y_scaler_data_min
        y_scaler.data_max_ = build.y_scaler_data_max
        y_scaler.data_range_ = build.y_scaler_data_range
        y_scaler.n_features_in_ = build.y_scaler_n_features_in
        y_scaler.n_samples_seen_ = build.y_scaler_n_samples_seen

        x_test = pd.DataFrame(
            data=np.full((self.lag, self.input_size), 0), columns=x_columns
        )
        y = np.zeros((self.lag, self.output_size))
        y = torch.FloatTensor(np.expand_dims(y, axis=0)).to(device)

        # test_period = []
        with torch.no_grad():
            while True:
                if len(input_queue.queue) > 0:
                    # start = time.time()

                    x_data = input_queue.get()
                    x_test = pd.concat(
                        [x_test, x_data[x_columns]], join="outer", axis=0
                    ).iloc[-self.lag :, :]
                    x_test_scaled = x_scaler.transform(x_test.to_numpy())
                    x = torch.FloatTensor(np.expand_dims(x_test_scaled, axis=0)).to(
                        device
                    )
                    z = repeater.forward(x, y)
                    y = torch.cat((y, torch.unsqueeze(z[:, -1, :], dim=0)), dim=1)[
                        :, -self.lag :, :
                    ]
                    y_test_scaled = np.squeeze(y.cpu().numpy(), axis=0)
                    y_test = y_scaler.inverse_transform(y_test_scaled)

                    df_run = pd.DataFrame(
                        np.hstack(
                            (
                                x_data.values[-1:, :],
                                y_test[-1:, :],
                            )
                        ),
                        columns=columns,
                    )
                    df_run.index = pd.to_datetime(x_data.index)
                    output_queue.put(df_run)

                    # end = time.time()
                    # test_period.append(end - start)

                if r.hget("sensor_{}".format(self.id), "state") == b"0":
                    break

    def transmit(self, signals, output_queue, org):
        self.client = InfluxDBClient(
            url=config.INFLUXDB_URL,
            token=config.INFLUXDB_TOKEN,
            org=org,
        )
        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        with app.app_context():
            columns, _, _ = self.get_fields(signals, "description")
        measurement = self.description
        tags = {"company_{}".format(self.company_id): "sensor_{}".format(self.id)}

        while True:
            if len(output_queue.queue) > 0:
                df = output_queue.get()
                df.columns = columns
                data = {
                    "measurement": measurement,
                    "tags": tags,
                    "time": str(df.index.values[0]),
                    "fields": df.to_dict("records").pop(),
                }

                point = Point.from_dict(data)
                write_api.write(bucket=config.INFLUXDB_BUCKET, record=point)

                # print("sensor_{}: {}".format(self.id, data["time"]))

            if r.hget("sensor_{}".format(self.id), "state") == b"0":
                break

        self.client.close()


class SensorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Sensor

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    sampling_period = ma.auto_field()
    input_size = ma.auto_field()
    output_size = ma.auto_field()
    created_date = ma.auto_field()
