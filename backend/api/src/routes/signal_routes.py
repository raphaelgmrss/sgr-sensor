from flask import Blueprint
from src.controllers.signal_controller import (
    create,
    read,
    read_all,
    update,
    delete,
    delete_all,
)

signal_bp = Blueprint("signal_bp", __name__, url_prefix="/api/signal")

signal_bp.route("", methods=["POST"])(create)
signal_bp.route("/<int:signal_id>", methods=["GET"])(read)
signal_bp.route("", methods=["GET"])(read_all)
signal_bp.route("/<int:signal_id>", methods=["PUT"])(update)
signal_bp.route("/<int:signal_id>", methods=["DELETE"])(delete)
signal_bp.route("", methods=["DELETE"])(delete_all)
