"""API endpoints for route calculation with the AI"""

from flask import Blueprint, jsonify, request

# commenting this line until the RL engine is ready
# from ia_ml.src.api.main import find_ai_route

paths_bp = Blueprint("paths", __name__)

@paths_bp.route("/calculate", methods=["POST"])
def get_path():
    """
    Endpoint for calculating the optimal route between two points and waypoints.
    Expects JSON body with keys:
      - start_node: [lng, lat]
      - end_node: [lng, lat]
      - waypoints: optional list of [lng, lat]
    """

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    start_node = data.get("start_node")
    end_node = data.get("end_node")
    waypoints = data.get("waypoints", [])

    if start_node is None or end_node is None:
        return jsonify({"error": "The 'start_node' and 'end_node' fields are required in JSON body"}), 400

    try:
        # validate start and end as coordinate pairs
        if not (isinstance(start_node, (list, tuple)) and len(start_node) >= 2):
            raise ValueError("start_node must be a [lng, lat] pair")
        if not (isinstance(end_node, (list, tuple)) and len(end_node) >= 2):
            raise ValueError("end_node must be a [lng, lat] pair")

        start_node = [float(start_node[0]), float(start_node[1])]
        end_node = [float(end_node[0]), float(end_node[1])]

        parsed_waypoints = []
        if isinstance(waypoints, (list, tuple)):
            for wp in waypoints:
                if not (isinstance(wp, (list, tuple)) and len(wp) >= 2):
                    raise ValueError("each waypoint must be a [lng, lat] pair")
                parsed_waypoints.append([float(wp[0]), float(wp[1])])
        else:
            raise ValueError("waypoints must be an array of [lng, lat] pairs")

        waypoints = parsed_waypoints
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    # commenting this line until the RL engine is ready
    # route_data = find_ai_route(start_node, waypoints, end_node)

    # --- INICIO: Bloque de código temporal para evitar errores ---
    route_data = {
        "coordinates": [
            [-64.349, -33.123],
            [-64.350, -33.124],
            [-64.351, -33.125]
        ],
        "duration": 130.0,
        "distance": 1100.5
    }
    # --- FIN: Bloque de código temporal ---

    if not route_data:
        return jsonify({"error": "A route could not be found with the provided parameters."}), 500

    
    response_data = {
        "route": [route_data],
        "waypoints": waypoints
    }

    return jsonify(response_data), 200
