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
device = "cuda" if torch.cuda.is_available() else "cpu"


class Sensor(db.Model):
    __tablename__ = "sensor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    sampling_period = db.Column(db.Integer, default=1)
    input_size = db.Column(db.Integer)
    output_size = db.Column(db.Integer)
    model_path = db.Column(db.String)
    state = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __init__(
        self, name, description, sampling_period, input_size, output_size, model_path
    ):
        self.name = name
        self.description = description
        self.sampling_period = sampling_period
        self.input_size = input_size
        self.output_size = output_size
        self.model_path = "../database/{}.pt".format(model_path)

    def get_fields(self, signals):
        x_columns = []
        y_columns = []
        columns = None

        for signal in signals:
            column = "signal_{}".format(signal.id)

            if signal.group == "input":
                x_columns.append(column)
            elif signal.group == "output":
                y_columns.append(column)

        columns = x_columns + y_columns

        return columns, x_columns, y_columns

    def clock(self, clock_event, kill_event):
        while True:
            clock_event.set()
            clock_event.clear()
            time.sleep(self.sampling_period)

            if kill_event.is_set():
                clock_event.set()
                clock_event.clear()
                break

    def receive(self, signals, input_queue, clock_event):
        with app.app_context():
            _, x_columns, _ = self.get_fields(signals)

        while True:
            clock_event.wait()

            data = [datetime.now().isoformat()]
            with app.app_context():
                for signal in signals:
                    if signal.group == "input":
                        data.append(signal.setpoint)

            df_input = (
                pd.DataFrame(
                    [data],
                    columns=["date_time"] + x_columns,
                )
                .set_index("date_time")
                .astype("float")
            )

            input_queue.put(df_input)

            if self.state == True:
                break

    def process(self, signals, input_queue, output_queue):
        repeater = torch.jit.load(self.model_path).to(device)
        with app.app_context():
            columns, x_columns, y_columns = self.get_fields(signals)

        feature_range = (-1, 1)

        x_scaler = MinMaxScaler(feature_range=feature_range)
        x_scaler.min_ = repeater.x_min_
        x_scaler.scale_ = repeater.x_scale_
        x_scaler.data_min_ = repeater.x_data_min_
        x_scaler.data_max_ = repeater.x_data_max_
        x_scaler.data_range_ = repeater.x_data_range_
        x_scaler.n_features_in_ = repeater.x_n_features_in_
        x_scaler.n_samples_seen_ = repeater.x_n_samples_seen_

        y_scaler = MinMaxScaler(feature_range=feature_range)
        y_scaler.min_ = repeater.y_min_
        y_scaler.scale_ = repeater.y_scale_
        y_scaler.data_min_ = repeater.y_data_min_
        y_scaler.data_max_ = repeater.y_data_max_
        y_scaler.data_range_ = repeater.y_data_range_
        y_scaler.n_features_in_ = repeater.y_n_features_in_
        y_scaler.n_samples_seen_ = repeater.y_n_samples_seen_

        x = pd.DataFrame(
            data=np.full((repeater.lag, self.input_size), 0), columns=x_columns
        )
        y_scaled = torch.FloatTensor(
            np.expand_dims(np.zeros((repeater.lag, self.output_size)), axis=0)
        )

        test_period = []
        while True:
            if len(input_queue.queue) > 0:
                start = time.time()

                x_data = input_queue.get()
                x = pd.concat([x, x_data[x_columns]], join="outer", axis=0).iloc[
                    -repeater.lag :, :
                ]
                x_scaled = x_scaler.transform(x.to_numpy())
                x_scaled = torch.FloatTensor(np.expand_dims(x_scaled, axis=0))
                z = repeater.forward(x_scaled, y_scaled)
                y_scaled = torch.cat(
                    (y_scaled, torch.unsqueeze(z[:, -1, :], dim=0)), dim=1
                )[:, -repeater.lag :, :]
                y = y_scaler.inverse_transform(
                    np.squeeze(y_scaled.cpu().detach().numpy(), axis=0)
                )

                df_output = pd.DataFrame(
                    np.hstack(
                        (
                            x_data.values[-1:, :],
                            y[-1:, :],
                        )
                    ),
                    columns=columns,
                )
                df_output.index = pd.to_datetime(x_data.index)
                output_queue.put(df_output)

                end = time.time()
                test_period.append(end - start)
                # print(end - start)
                print(df_output)

    #         if r.hget("sensor_{}".format(self.id), "state") == b"0":
    #             break

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
    state = ma.auto_field()
    created_date = ma.auto_field()
