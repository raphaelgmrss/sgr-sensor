from datetime import datetime
from flask_marshmallow import Marshmallow
from src import db

ma = Marshmallow()


class Signal(db.Model):
    __tablename__ = "signal"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id"), nullable=False)
    name = db.Column(db.String)
    description = db.Column(db.String)
    unit = db.Column(db.String)
    group = db.Column(db.String)
    setpoint = db.Column(db.Float)
    setpoint_min = db.Column(db.Float)
    setpoint_max = db.Column(db.Float)
    setpoint_step = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.now)
    sensor = db.relationship("Sensor", backref="signals")

    def __init__(
        self,
        sensor_id,
        name,
        description,
        unit,
        group,
        setpoint,
        setpoint_min,
        setpoint_max,
        setpoint_step,
    ):
        self.sensor_id = sensor_id
        self.name = name
        self.description = description
        self.unit = unit
        self.group = group
        self.setpoint = setpoint
        self.setpoint_min = setpoint_min
        self.setpoint_max = setpoint_max
        self.setpoint_step = setpoint_step


class SignalSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Signal

    id = ma.auto_field()
    sensor_id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    unit = ma.auto_field()
    group = ma.auto_field()
    setpoint = ma.auto_field()
    setpoint_min = ma.auto_field()
    setpoint_max = ma.auto_field()
    setpoint_step = ma.auto_field()
    created_date = ma.auto_field()
