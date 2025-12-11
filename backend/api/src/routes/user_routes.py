from flask import Blueprint
from src.controllers.user_controller import (
    create,
    read,
    read_all,
    update,
    delete,
    delete_all,
)

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/user")

user_bp.route("", methods=["POST"])(create)
user_bp.route("/<int:user_id>", methods=["GET"])(read)
user_bp.route("", methods=["GET"])(read_all)
user_bp.route("/<int:user_id>", methods=["PUT"])(update)
user_bp.route("/<int:user_id>", methods=["DELETE"])(delete)
user_bp.route("", methods=["DELETE"])(delete_all)
