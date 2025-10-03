"""API endpoints for user-related operations."""

from flask import Blueprint, jsonify, abort
from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

bp = Blueprint("users", __name__)

@bp.route("/", methods=["GET"])
def list_users():
    """Return all users as JSON."""
    with SessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)
        users = user_service.list_users()
    return jsonify(users)

@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Return a single user by ID as JSON."""
    with SessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)
        user = user_service.get_user(user_id)
        if not user:
            abort(404, description="User not found")
    return jsonify(user)
