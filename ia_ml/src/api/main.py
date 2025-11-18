# ia_ml/api/main.py

import sys
from pathlib import Path
from typing import Dict, List, Optional
import os
import networkx as nx

# Add repo root to sys.path so ia_ml package is importable
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ia_ml.src.training.run_inference import run_episode
from ia_ml.src.data.download_graph import get_graph_relabel, load_subgraph_from_file


def find_route_with_astar(
    start_node_coord: List[float],
    waypoints_coords: List[List[float]],
    end_node_coord: List[float]
) -> Optional[Dict]:
    """
    Calcula una ruta óptima usando A* (algoritmo clásico).
    Útil como fallback o para desarrollo antes de tener el modelo entrenado.
    
    Args:
        start_node_coord: [lon, lat] del nodo inicial
        waypoints_coords: lista de [lon, lat] para cada waypoint
        end_node_coord: [lon, lat] del nodo destino

    Returns:
        Diccionario con coordinates, duration y distance, o None si falla
    """
    try:
        # Cargar el subgrafo
        ia_ml_root = Path(__file__).resolve().parent.parent.parent
        subgraph_path = ia_ml_root / "scripts" / "subgraph.graphml"
        
        if not subgraph_path.exists():
            raise FileNotFoundError(f"Subgrafo no encontrado en {subgraph_path}")
        
        graph, _, _ = load_subgraph_from_file(str(subgraph_path))

        # Función auxiliar para encontrar el nodo más cercano
        def get_nearest_node(coord):
            min_node = min(graph.nodes, key=lambda n: (
                (graph.nodes[n]['x'] - coord[0])**2 + (graph.nodes[n]['y'] - coord[1])**2
            ))
            return min_node

        start_node = get_nearest_node(start_node_coord)
        waypoint_nodes = [get_nearest_node(wp) for wp in waypoints_coords]
        end_node = get_nearest_node(end_node_coord)

        # Construir la ruta completa: start -> waypoints (en orden) -> end
        full_path = []
        current = start_node
        nodes_to_visit = waypoint_nodes + [end_node]
        
        total_distance = 0.0
        
        for next_node in nodes_to_visit:
            try:
                # Usar A* con peso 'length' o 'travel_time' si existe
                weight = 'travel_time' if 'travel_time' in graph.edges[list(graph.edges)[0]] else 'length'
                segment = nx.astar_path(graph, current, next_node, weight=weight)
                
                # Agregar segmento (sin duplicar el nodo de conexión)
                if full_path:
                    full_path.extend(segment[1:])
                else:
                    full_path.extend(segment)
                
                # Calcular distancia del segmento
                segment_distance = nx.astar_path_length(graph, current, next_node, weight=weight)
                total_distance += segment_distance
                
                current = next_node
            except nx.NetworkXNoPath:
                print(f"[A*] No hay camino entre {current} y {next_node}")
                return None

        # Convertir nodos a coordenadas
        coordinates = [[graph.nodes[n]["x"], graph.nodes[n]["y"]] for n in full_path]
        
        # Estimar duración (asumiendo velocidad promedio)
        duration = total_distance * 1.2  # factor de conversión simple
        
        return {
            "coordinates": coordinates,
            "duration": duration,
            "distance": total_distance
        }

    except Exception as e:
        print(f"[A* Error] No se pudo generar la ruta: {e}")
        return None


def find_ai_route(
    start_node_coord: List[float],
    waypoints_coords: List[List[float]],
    end_node_coord: List[float],
    use_astar_fallback: bool = True
) -> Optional[Dict]:
    """
    Calcula una ruta óptima usando el modelo PPO entrenado.
    Si el modelo no está disponible y use_astar_fallback=True, usa A*.
    
    Args:
        start_node_coord: [lon, lat] del nodo inicial
        waypoints_coords: lista de [lon, lat] para cada waypoint
        end_node_coord: [lon, lat] del nodo destino
        use_astar_fallback: Si es True, usa A* cuando el modelo no esté disponible

    Devuelve un diccionario con:
    {
        "coordinates": [[lon1, lat1], [lon2, lat2], ...],
        "duration": float,
        "distance": float
    }
    o None si no se encuentra una ruta válida.
    """

    # Verificar si el modelo está disponible
    ia_ml_root = Path(__file__).resolve().parent.parent.parent
    model_path = ia_ml_root / "logs" / "best_model_masked" / "best_model.zip"
    
    if not model_path.exists():
        if use_astar_fallback:
            print("[Info] Modelo no disponible, usando A* como fallback")
            return find_route_with_astar(start_node_coord, waypoints_coords, end_node_coord)
        else:
            print("[Error] Modelo no encontrado y fallback deshabilitado")
            return None

    try:
        # Cargar el subgrafo usado para entrenar el modelo
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
            if use_astar_fallback:
                print("[Info] Modelo no encontró ruta, usando A* como fallback")
                return find_route_with_astar(start_node_coord, waypoints_coords, end_node_coord)
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
        print(f"[Error] Error al ejecutar modelo PPO: {e}")
        if use_astar_fallback:
            print("[Info] Usando A* como fallback debido a error")
            return find_route_with_astar(start_node_coord, waypoints_coords, end_node_coord)
        return None

