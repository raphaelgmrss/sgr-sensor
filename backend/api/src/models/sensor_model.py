import uuid
from datetime import datetime
import time

from flask_marshmallow import Marshmallow
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import torch
from sqlalchemy import create_engine

from src import app, db, engine


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
    buffer = db.Column(db.Integer)
    model_path = db.Column(db.String)
    state = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __init__(
        self,
        name,
        description,
        sampling_period,
        input_size,
        output_size,
        buffer,
        model_path,
    ):
        self.name = name
        self.description = description
        self.sampling_period = sampling_period
        self.input_size = input_size
        self.output_size = output_size
        self.buffer = buffer
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

    def receive(self, Signal, input_queue, clock_event):

        with app.app_context():
            signals = Signal.query.filter_by(sensor_id=self.id).order_by(
                Signal.id.asc()
            )
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

            if not self.state:
                break

    def process(self, Signal, input_queue, output_queue, clock_event):
        repeater = torch.jit.load(self.model_path).to(device)

        with app.app_context():
            signals = Signal.query.filter_by(sensor_id=self.id).order_by(
                Signal.id.asc()
            )
            columns, x_columns, _ = self.get_fields(signals)

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

        while True:
            clock_event.wait()
            if len(input_queue.queue) > 0:

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

            if not self.state:
                break

    def transmit(self, Signal, output_queue, clock_event):
        engine = create_engine("sqlite:///../database/database.db")
        table = "data"

        with app.app_context():
            signals = Signal.query.filter_by(sensor_id=self.id).order_by(
                Signal.id.asc()
            )
            columns, _, _ = self.get_fields(signals)

        df_data = pd.DataFrame(
            data=np.full((self.buffer, len(columns)), 0), columns=columns
        )
        df_data.index = pd.date_range(
            end=pd.to_datetime("now"), periods=self.buffer, freq="1s"
        )
        df_data.index.name = "date_time"
        df_data.to_sql(
            table, con=engine, if_exists="replace", index=False, index_label="date_time"
        )

        while True:
            clock_event.wait()
            if len(output_queue.queue) > 0:
                df_output = output_queue.get()
                df_data = pd.concat([df_data, df_output], axis=0)
                if len(df_data) > self.buffer:
                    df_data = df_data.iloc[-self.buffer :]
                df_data.to_sql(table, con=engine, if_exists="replace", index=True)

            if not self.state:
                break


class SensorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Sensor

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    sampling_period = ma.auto_field()
    input_size = ma.auto_field()
    output_size = ma.auto_field()
    buffer = ma.auto_field()
    state = ma.auto_field()
    created_date = ma.auto_field()
