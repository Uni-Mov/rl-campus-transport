"""API endpoints for route calculation with the AI"""

from flask import Blueprint, jsonify, request

paths_bp = Blueprint("paths", __name__)

# Simulation of the AI/ML model function
# This is a placeholder. This is where we would call the real model
def call_ai_model(start_node, end_node):
    """
    Mock function that simulates the AI.
    In the future, this function will import and execute the code in the /ia_ml folder.
    """
    return {
        "routes": [
            {
                "coordinates": [
                    [-64.349323, -33.123203],
                    [-64.349316, -33.123246],
                    [-64.349561, -33.124013],
                    [-64.349619, -33.124079],
                    [-64.349687, -33.124143]
                ],
                "duration": 127.5,
                "distance": 1057.8
            }
        ],
        "waypoints": []
    }

@paths_bp.route("/calculate", methods=["GET"])
def get_path():
    """
    Endpoint for calculating the optimal route between two points.
    Receives the start and end nodes as URL parameters.
    """

    start_node = request.args.get("start_node")
    end_node = request.args.get("end_node")

    if not start_node or not end_node:
        return jsonify({"error": "The 'start_node' and 'end_node' parameters are required"}), 400

    path_data = call_ai_model(start_node, end_node)

    return jsonify(path_data), 200
