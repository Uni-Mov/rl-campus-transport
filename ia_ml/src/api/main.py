# ia_ml/api/main.py

from pathlib import Path
from typing import Dict, List, Optional
import os

from src.training.run_inference import run_episode
from src.data.download_graph import get_graph_relabel


def find_ai_route(
    start_node_coord: float,
    waypoints_coords: List[float],
    end_node_coord: float
) -> Optional[Dict]:
    """
    Calcula una ruta óptima usando el modelo PPO entrenado.

    Devuelve un diccionario con:
    {
        "coordinates": [[lon1, lat1], [lon2, lat2], ...],
        "duration": float,
        "distance": float
    }
    o None si no se encuentra una ruta válida.
    """

    try:
        # Cargar el grafo del mapa
        place = "Guatimozin, Cordoba, Argentina"  
        graph, node_to_idx, idx_to_node = get_graph_relabel(place)

        # Obtener los nodos más cercanos a las coordenadas
        def get_nearest_node(coord):
            # coord = [lon, lat]
            min_node = min(graph.nodes, key=lambda n: (
                (graph.nodes[n]['x'] - coord[0])**2 + (graph.nodes[n]['y'] - coord[1])**2
            ))
            return min_node

        start_node = get_nearest_node(start_node_coord)
        waypoints = [get_nearest_node(wp) for wp in waypoints_coords]
        end_node = get_nearest_node(end_node_coord)

        # Ruta al modelo entrenado
        model_path = os.path.join(Path(__file__).resolve().parents[1], "ppo_waypoint_masked.zip")

        # Ejecutar un episodio con el modelo PPO
        result = run_episode(
            place=place,
            model_path=model_path,
            start=start_node,
            waypoints=waypoints,
            destination=end_node,
            deterministic=True
        )

        # Si no llegó al destino, devolver None
        if not result.get("done", False):
            return None

        # Extraer coordenadas
        path_nodes = result.get("path", [])
        coordinates = [[graph.nodes[n]["x"], graph.nodes[n]["y"]] for n in path_nodes]

        # Calcular distancia y duración (pueden venir en info o se calculan)
        info = result.get("info", {})
        distance = info.get("total_distance", len(path_nodes))
        duration = info.get("total_duration", distance * 1.2)

        return {
            "coordinates": coordinates,
            "duration": duration,
            "distance": distance
        }

    except Exception as e:
        print(f"[Error] No se pudo generar la ruta: {e}")
        return None

