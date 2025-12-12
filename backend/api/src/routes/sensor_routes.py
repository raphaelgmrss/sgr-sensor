from flask import Blueprint
from src.controllers.sensor_controller import (
    create,
    read,
    read_all,
    update,
    delete,
    delete_all,
    get_signals,
    start,
    stop,
    get_state,
    set_state,
    set_values,
)

sensor_bp = Blueprint("sensor_bp", __name__, url_prefix="/api/sensor")

sensor_bp.route("", methods=["POST"])(create)
sensor_bp.route("/<int:sensor_id>", methods=["GET"])(read)
sensor_bp.route("", methods=["GET"])(read_all)
sensor_bp.route("/<int:sensor_id>", methods=["PUT"])(update)
sensor_bp.route("/<int:sensor_id>", methods=["DELETE"])(delete)
sensor_bp.route("", methods=["DELETE"])(delete_all)
sensor_bp.route("/<int:sensor_id>/signals", methods=["GET"])(get_signals)
sensor_bp.route("/<int:sensor_id>/start", methods=["GET"])(start)
sensor_bp.route("/<int:sensor_id>/stop", methods=["GET"])(stop)
sensor_bp.route("/<int:sensor_id>/state", methods=["GET"])(get_state)
sensor_bp.route("/<int:sensor_id>/state/<int:state>", methods=["GET"])(set_state)
sensor_bp.route("/<int:sensor_id>/values", methods=["POST"])(set_values)
