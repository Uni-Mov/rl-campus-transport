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

    if user is None:
        abort(404, description="User not found")

    return jsonify(user)

@bp.route("/", methods=["POST"])
def create_user():
    """Create a new user from frontend data."""
    data = request.get_json()

    if not data:
        abort(400, description="Invalid or missing JSON body")

    required = ["first_name", "last_name", "dni", "email", "password", "role"]
    if not all(field in data for field in required):
        abort(400, description="Missing required fields")

    new_user_data = None

    with SessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)

        try:
            new_user_model = user_service.create_user(
                first_name=data["first_name"],
                last_name=data["last_name"],
                dni=data["dni"],
                email=data["email"],
                password=data["password"],
                role=data["role"],
            )

            new_user_data = user_service._serialize(new_user_model)

        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            session.rollback()
            abort(500, description="Internal Server Error during user creation")

    return jsonify(new_user_data), 201
