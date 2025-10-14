"""API endpoints for route calculation with the AI"""

from flask import Blueprint, jsonify, request

# TODO: Cuando el equipo de IA/RL implemente "find_ai_route", se debera importar ACA!
# from ia_ml.main import find_ai_route #EJEMPLO DE IMPORTACION

paths_bp = Blueprint("paths", __name__)

@paths_bp.route("/calculate", methods=["GET"])
def get_path():
    """
    Endpoint for calculating the optimal route between two points and waypoints.
    Receives the start and end nodes and waypoints as URL parameters.
    """

    start_node_srt = request.args.get("start_node")
    end_node_srt = request.args.get("end_node")

    if not start_node_srt or not end_node_srt:
        return jsonify({"error": "The 'start_node' and 'end_node' parameters are required"}), 400

    try:
        start_node = float(start_node_srt)
        end_node = float(end_node_srt)
        waypoints_srt = request.args.get("waypoints", "")
        waypoints = [float(wp) for wp in waypoints_srt.split(",")]
    except ValueError:
        return jsonify({"error": "Parameters must be valid numbers (integers or decimals)."}) , 400

    # 2. Llamar al modelo de IA real
    # TODO: Descomentar y ajustar esta línea cuando la función de IA esté disponible.
    # route_data = find_ai_route(
    #     start_node_coord=start_node, # Nombres de parámetro sugeridos
    #     waypoints_coords=waypoints,
    #     end_node_coord=end_node
    # )

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
