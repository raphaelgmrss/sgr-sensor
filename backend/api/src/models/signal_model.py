from datetime import datetime
from flask_marshmallow import Marshmallow
from src import db

ma = Marshmallow()


class Signal(db.Model):
    __tablename__ = "signal"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    unit = db.Column(db.String)
    value = db.Column(db.Float)
    setpoint = db.Column(db.Float)
    setpoint_min = db.Column(db.Float)
    setpoint_max = db.Column(db.Float)
    setpoint_step = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __init__(
        self,
        name,
        description,
        unit,
        setpoint,
        setpoint_min,
        setpoint_max,
        setpoint_step,
    ):
        self.name = name
        self.description = description
        self.unit = unit
        self.setpoint = setpoint
        self.setpoint_min = setpoint_min
        self.setpoint_max = setpoint_max
        self.setpoint_step = setpoint_step


class SignalSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "description",
            "unit",
            "value",
            "setpoint",
            "setpoint_min",
            "setpoint_max",
            "setpoint_step",
            "created_date",
        )
