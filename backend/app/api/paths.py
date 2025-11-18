"""API endpoints for route calculation with the AI"""

from flask import Blueprint, jsonify, request

from ia_ml.src.api.main import find_ai_route, find_route_with_astar

paths_bp = Blueprint("paths", __name__)

@paths_bp.route("/calculate", methods=["GET", "POST"])
def get_path():
    """
    Endpoint for calculating the optimal route between two points and waypoints.
    
    GET: Expects query parameters:
      - start_node: "lon,lat"
      - end_node: "lon,lat"  
      - waypoints: "lon1,lat1;lon2,lat2;..." (optional)
      
    POST: Expects JSON body with keys:
      - start_node: [lng, lat]
      - end_node: [lng, lat]
      - waypoints: optional list of [lng, lat]
    """
    
    # Handle GET requests with query parameters
    if request.method == "GET":
        start_node_str = request.args.get("start_node")
        end_node_str = request.args.get("end_node")
        
        if not start_node_str or not end_node_str:
            return jsonify({"error": "The 'start_node' and 'end_node' parameters are required"}), 400
        
        try:
            # Parse start_node y end_node como "lon,lat"
            start_coords = [float(x) for x in start_node_str.split(",")]
            end_coords = [float(x) for x in end_node_str.split(",")]
            
            if len(start_coords) != 2 or len(end_coords) != 2:
                return jsonify({"error": "Coordinates must be in format 'lon,lat'"}), 400
            
            # Parse waypoints como "lon1,lat1;lon2,lat2;..."
            waypoints_str = request.args.get("waypoints", "")
            waypoints = []
            if waypoints_str:
                for wp_str in waypoints_str.split(";"):
                    wp_coords = [float(x) for x in wp_str.split(",")]
                    if len(wp_coords) != 2:
                        return jsonify({"error": "Each waypoint must be in format 'lon,lat'"}), 400
                    waypoints.append(wp_coords)
        except ValueError:
            return jsonify({"error": "Parameters must be valid numbers."}), 400
            
        start_node = start_coords
        end_node = end_coords
        
    # Handle POST requests with JSON body
    else:
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

    # Call AI route finder (with A* fallback)
    try:
        route_data = find_ai_route(start_node, waypoints, end_node, use_astar_fallback=True)
        if not route_data:
            route_data = find_route_with_astar(start_node, waypoints, end_node)
    except Exception as e:
        try:
            route_data = find_route_with_astar(start_node, waypoints, end_node)
        except Exception:
            return jsonify({"error": "Error calculating route"}), 500

    if not route_data:
        return jsonify({"error": "A route could not be found with the provided parameters."}), 500

    
    response_data = {
        "route": [route_data],
        "waypoints": waypoints
    }

    return jsonify(response_data), 200
