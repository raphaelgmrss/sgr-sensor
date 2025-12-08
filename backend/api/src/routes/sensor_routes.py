from flask import Blueprint
from src.controllers.sensor_controller import (
    create,
    read,
    read_all,
    update,
    delete,
    delete_all,
    get_signals,
    get_builds,
    build,
    start,
    stop,
    reset,
    get_state,
    set_state,
    get_states,
    get_mode,
    set_mode,
    get_data,
    set_variables,
)

sensor_bp = Blueprint("sensor_bp", __name__, url_prefix="/api/sensor")

sensor_bp.route("", methods=["POST"])(create)
sensor_bp.route("/<int:sensor_id>", methods=["GET"])(read)
sensor_bp.route("", methods=["GET"])(read_all)
sensor_bp.route("/<int:sensor_id>", methods=["PUT"])(update)
sensor_bp.route("/<int:sensor_id>", methods=["DELETE"])(delete)
sensor_bp.route("", methods=["DELETE"])(delete_all)
sensor_bp.route("/<int:sensor_id>/signals", methods=["GET"])(get_signals)
sensor_bp.route("/<int:sensor_id>/builds", methods=["GET"])(get_builds)
sensor_bp.route("/<int:sensor_id>/build", methods=["GET"])(build)
sensor_bp.route("/<int:sensor_id>/start", methods=["GET"])(start)
sensor_bp.route("/<int:sensor_id>/stop", methods=["GET"])(stop)
sensor_bp.route("/reset", methods=["GET"])(reset)
sensor_bp.route("/<int:sensor_id>/state", methods=["GET"])(get_state)
sensor_bp.route("/<int:sensor_id>/state/<int:state>", methods=["GET"])(set_state)
sensor_bp.route("/states", methods=["GET"])(get_states)
sensor_bp.route("/<int:sensor_id>/mode", methods=["GET"])(get_mode)
sensor_bp.route("/<int:sensor_id>/mode/<int:mode>", methods=["GET"])(set_mode)
sensor_bp.route("<int:sensor_id>/data/<start_date>/<end_date>", methods=["GET"])(
    get_data
)
sensor_bp.route("/variables", methods=["POST"])(set_variables)
