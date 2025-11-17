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
        # Parse start_node y end_node como "lon,lat"
        start_coords = [float(x) for x in start_node_srt.split(",")]
        end_coords = [float(x) for x in end_node_srt.split(",")]
        
        if len(start_coords) != 2 or len(end_coords) != 2:
            return jsonify({"error": "Coordinates must be in format 'lon,lat'"}), 400
        
        # Parse waypoints como "lon1,lat1;lon2,lat2;..."
        waypoints_srt = request.args.get("waypoints", "")
        waypoints = []
        if waypoints_srt:
            for wp_str in waypoints_srt.split(";"):
                wp_coords = [float(x) for x in wp_str.split(",")]
                if len(wp_coords) != 2:
                    return jsonify({"error": "Each waypoint must be in format 'lon,lat'"}), 400
                waypoints.append(wp_coords)
    except ValueError:
        return jsonify({"error": "Parameters must be valid numbers (integers or decimals)."}), 400

    route_data = find_ai_route(start_coords, waypoints, end_coords)

    if not route_data:
        return jsonify({"error": "A route could not be found with the provided parameters."}), 500

    
    response_data = {
        "route": [route_data],
        "waypoints": waypoints
    }

    return jsonify(response_data), 200
