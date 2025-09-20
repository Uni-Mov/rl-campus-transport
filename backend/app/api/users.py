from flask import Blueprint, jsonify

bp = Blueprint("users", __name__)

@bp.route("/", methods=["GET"])
def list_users():
    return jsonify({"users": []})
