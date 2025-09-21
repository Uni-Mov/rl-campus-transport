from flask import Blueprint, jsonify

bp = Blueprint("users", __name__)

@bp.route("/", methods=["GET"])
def list_users():
    return jsonify([{
        "id": 1,
        "name": "Juan Pérez",
        "email": "juan.perez@ejemplo.com"
    }, {
        "id": 2,
        "name": "María García", 
        "email": "maria.garcia@ejemplo.com"
    }])
