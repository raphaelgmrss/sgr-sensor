from flask import Blueprint

from src.controllers.auth_controller import (
    login,
    restore_password,
)

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

auth_bp.route("/login", methods=["POST"])(login)
auth_bp.route("/password/restore", methods=["POST"])(restore_password)
