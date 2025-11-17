# ia_ml/api/main.py

import sys
from pathlib import Path
from typing import Dict, List, Optional
import os

# Add repo root to sys.path so ia_ml package is importable
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ia_ml.src.training.run_inference import run_episode
from ia_ml.src.data.download_graph import get_graph_relabel, load_subgraph_from_file


def find_ai_route(
    start_node_coord: List[float],
    waypoints_coords: List[List[float]],
    end_node_coord: List[float]
) -> Optional[Dict]:
    """
    Calcula una ruta óptima usando el modelo PPO entrenado.
    
    Args:
        start_node_coord: [lon, lat] del nodo inicial
        waypoints_coords: lista de [lon, lat] para cada waypoint
        end_node_coord: [lon, lat] del nodo destino

    Devuelve un diccionario con:
    {
        "coordinates": [[lon1, lat1], [lon2, lat2], ...],
        "duration": float,
        "distance": float
    }
    o None si no se encuentra una ruta válida.
    """

    try:
        # Cargar el subgrafo usado para entrenar el modelo
        ia_ml_root = Path(__file__).resolve().parent.parent.parent  # De ia_ml/src/api a ia_ml
        subgraph_path = ia_ml_root / "scripts" / "subgraph.graphml"
        
        if not subgraph_path.exists():
            raise FileNotFoundError(f"Subgrafo no encontrado en {subgraph_path}")
        
        graph, node_to_idx, idx_to_node = load_subgraph_from_file(str(subgraph_path))

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

        # Ruta al modelo entrenado (buscar desde ia_ml/src/api subiendo a ia_ml y luego logs)
        ia_ml_root = Path(__file__).resolve().parent.parent.parent  # De ia_ml/src/api a ia_ml
        model_path = ia_ml_root / "logs" / "best_model_masked" / "best_model.zip"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado en {model_path}")

        # Ejecutar un episodio con el modelo PPO
        result = run_episode(
            graph=graph,
            node_to_idx=node_to_idx,
            idx_to_node=idx_to_node,
            model_path=str(model_path),
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

