import numpy as np
import networkx as nx
from typing import Dict, Any, Optional

# mapeo de highway types a códigos jerárquicos (mayor = más importante)
HIGHWAY_HIERARCHY = {
    'motorway': 6, 'motorway_link': 5,
    'trunk': 5, 'trunk_link': 4,
    'primary': 4, 'primary_link': 3,
    'secondary': 3, 'secondary_link': 2,
    'tertiary': 2, 'tertiary_link': 1,
    'residential': 1, 'living_street': 1,
    'unclassified': 0, 'service': 0,
}

# mapeo de surface types a scores (mayor = mejor calidad)
SURFACE_SCORES = {
    'paved': 1.0, 'asphalt': 1.0, 'concrete': 1.0,
    'paving_stones': 0.9, 'cobblestone': 0.8,
    'compacted': 0.7, 'gravel': 0.6,
    'dirt': 0.4, 'sand': 0.3, 'unpaved': 0.5,
    'grass': 0.2, 'ground': 0.3,
}

def _extract_maxspeed(edge_data: Dict[str, Any]) -> Optional[float]:
    """extrae maxspeed en km/h, convirtiendo diferentes formatos."""
    maxspeed = edge_data.get("maxspeed")
    if maxspeed is None:
        return None
    
    # si es número, asumir km/h
    if isinstance(maxspeed, (int, float)):
        return float(maxspeed)
    
    # si es string, parsear (ej: "50 km/h" -> 50, "50" -> 50)
    if isinstance(maxspeed, str):
        try:
            # remover "km/h", "mph", etc.
            cleaned = maxspeed.lower().replace("km/h", "").replace("mph", "").strip()
            # intentar extraer número
            for part in cleaned.split():
                try:
                    return float(part)
                except ValueError:
                    continue
        except Exception:
            pass
    
    return None

def _get_highway_code(edge_data: Dict[str, Any]) -> float:
    """convierte highway type a código jerárquico normalizado."""
    highway = edge_data.get("highway")
    if highway is None:
        return 0.0
    if isinstance(highway, list):
        highway = highway[0] if highway else None
    if highway is None:
        return 0.0
    return float(HIGHWAY_HIERARCHY.get(str(highway).lower(), 0.0)) / 6.0  # normalizado a [0, 1]

def _get_surface_score(edge_data: Dict[str, Any]) -> float:
    """obtiene score de superficie (0-1, mayor = mejor)."""
    surface = edge_data.get("surface")
    if surface is None:
        return 0.5  # default: calidad media
    if isinstance(surface, list):
        surface = surface[0] if surface else None
    if surface is None:
        return 0.5
    return SURFACE_SCORES.get(str(surface).lower(), 0.5)

def _get_oneway_flag(edge_data: Dict[str, Any]) -> float:
    """retorna 1.0 si es oneway, 0.0 si no."""
    oneway = edge_data.get("oneway", False)
    if isinstance(oneway, bool):
        return 1.0 if oneway else 0.0
    if isinstance(oneway, str):
        oneway_lower = oneway.lower()
        return 1.0 if oneway_lower in ("true", "yes", "1") else 0.0
    return 0.0

def _calculate_travel_time(edge_data: Dict[str, Any], default_speed_kmh: float = 50.0) -> float:
    """calcula travel_time en segundos.
    
    prioridad:
    1. usa travel_time si ya existe (calculado por osmnx)
    2. usa speed_kph si existe (de osmnx add_edge_speeds)
    3. calcula desde length y maxspeed
    4. usa default_speed_kmh si no hay datos
    """
    length = edge_data.get("length")
    if length is None:
        return 0.0
    
    length_m = float(length)
    
    # prioridad 1: travel_time calculado por osmnx
    travel_time = edge_data.get("travel_time")
    if travel_time is not None:
        return float(travel_time)
    
    # prioridad 2: speed_kph de osmnx add_edge_speeds
    speed_kph = edge_data.get("speed_kph")
    if speed_kph is not None:
        speed_ms = float(speed_kph) / 3.6
        return length_m / speed_ms if speed_ms > 0 else 0.0
    
    # prioridad 3: calcular desde maxspeed
    maxspeed_kmh = _extract_maxspeed(edge_data)
    if maxspeed_kmh is None:
        maxspeed_kmh = default_speed_kmh
    
    # convertir km/h a m/s y calcular tiempo
    speed_ms = maxspeed_kmh / 3.6
    travel_time_sec = length_m / speed_ms if speed_ms > 0 else 0.0
    
    return travel_time_sec

def _normalize_edge_features(graph: nx.MultiDiGraph) -> Dict[tuple, Dict[str, float]]:
    """normaliza características de todos los edges y retorna un diccionario.
    
    returns:
        dict[(u, v, key), {feature_name: normalized_value}]
    """
    # primero, recopilar todos los valores para normalización
    all_lengths = []
    all_maxspeeds = []
    all_lanes = []
    all_travel_times = []
    
    for u, v, key, attrs in graph.edges(keys=True, data=True):
        length = attrs.get("length")
        if length is not None:
            all_lengths.append(float(length))
        
        maxspeed = _extract_maxspeed(attrs)
        if maxspeed is not None:
            all_maxspeeds.append(maxspeed)
        
        lanes = attrs.get("lanes")
        if lanes is not None:
            try:
                if isinstance(lanes, (list, tuple)):
                    lanes = lanes[0] if lanes else None
                if lanes is not None:
                    all_lanes.append(float(lanes))
            except (ValueError, TypeError):
                pass
        
        travel_time = _calculate_travel_time(attrs)
        if travel_time > 0:
            all_travel_times.append(travel_time)
    
    # calcular rangos para normalización
    length_max = max(all_lengths) if all_lengths else 1.0
    maxspeed_max = max(all_maxspeeds) if all_maxspeeds else 1.0
    lanes_max = max(all_lanes) if all_lanes else 1.0
    travel_time_max = max(all_travel_times) if all_travel_times else 1.0
    
    # normalizar cada edge
    normalized = {}
    for u, v, key, attrs in graph.edges(keys=True, data=True):
        length = float(attrs.get("length", 0.0))
        maxspeed = _extract_maxspeed(attrs)
        maxspeed_norm = float(maxspeed / maxspeed_max) if maxspeed is not None else 0.0
        
        lanes = attrs.get("lanes")
        lanes_value = 0.0
        if lanes is not None:
            try:
                if isinstance(lanes, (list, tuple)):
                    lanes_value = float(lanes[0]) if lanes else 0.0
                else:
                    lanes_value = float(lanes)
            except (ValueError, TypeError):
                lanes_value = 0.0
        lanes_norm = lanes_value / lanes_max if lanes_max > 0 else 0.0
        
        highway_code = _get_highway_code(attrs)
        surface_score = _get_surface_score(attrs)
        oneway_flag = _get_oneway_flag(attrs)
        travel_time = _calculate_travel_time(attrs)
        travel_time_norm = travel_time / travel_time_max if travel_time_max > 0 else 0.0
        
        normalized[(u, v, key)] = {
            "length": length,
            "maxspeed_norm": maxspeed_norm,
            "lanes_norm": lanes_norm,
            "highway_code": highway_code,
            "surface_score": surface_score,
            "oneway_flag": oneway_flag,
            "travel_time": travel_time,
            "travel_time_norm": travel_time_norm,
        }
    
    return normalized

def _calculate_intersection_density(node: int, graph: nx.MultiDiGraph, radius_nodes: int = 2) -> float:
    """calcula densidad de intersecciones alrededor de un nodo.
    
    cuenta cuántos nodos únicos están a distancia <= radius_nodes.
    """
    if radius_nodes <= 0:
        return 0.0
    
    visited = {node}
    current_level = {node}
    
    for _ in range(radius_nodes):
        next_level = set()
        for n in current_level:
            for neighbor in graph.neighbors(n):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.add(neighbor)
        current_level = next_level
        if not current_level:
            break
    
    # normalizar por número máximo posible (heurística)
    return float(len(visited) - 1) / (radius_nodes * 10.0)  # aproximación

def _calculate_road_hierarchy(node: int, graph: nx.MultiDiGraph) -> float:
    """calcula jerarquía de calles promedio en edges incidentes al nodo."""
    edges_incident = []
    for u, v, key, attrs in graph.edges(node, keys=True, data=True):
        edges_incident.append(attrs)
    
    if not edges_incident:
        return 0.0
    
    hierarchy_sum = 0.0
    for attrs in edges_incident:
        hierarchy_sum += _get_highway_code(attrs)
    
    return hierarchy_sum / len(edges_incident)

def build_node_embeddings(graph: nx.MultiDiGraph) -> Dict[str, np.ndarray]:
    """genera embeddings ampliados por nodo incluyendo características de edges.
    
    embeddings incluyen:
    - características estructurales del nodo (x, y, grado, etc.)
    - características de edges promediadas (length, maxspeed_norm, lanes_norm, etc.)
    - travel_time calculado y normalizado
    - intersection_density y road_hierarchy
    
    formato del embedding:
    [x_norm, y_norm, deg_norm, in_deg, out_deg, neighbor_count,
     avg_neighbor_deg, max_neighbor_deg, min_neighbor_deg, neighbor_deg_std,
     degree_centrality, betweenness_approx, network_density,
     length_avg, maxspeed_norm_avg, lanes_norm_avg, highway_code_avg,
     surface_score_avg, oneway_flag_avg, travel_time_norm_avg,
     intersection_density, road_hierarchy]
    """
    if graph.number_of_nodes() == 0:
        return {}

    nodes = list(graph.nodes(data=True))
    n_nodes = graph.number_of_nodes()

    # normalizar características de edges
    edge_features = _normalize_edge_features(graph)
    
    # normalizar coordenadas
    xs = np.array([float(data.get("x", 0.0)) for _, data in nodes], dtype=np.float32)
    ys = np.array([float(data.get("y", 0.0)) for _, data in nodes], dtype=np.float32)

    x_min, x_max = xs.min(initial=0.0), xs.max(initial=0.0)
    y_min, y_max = ys.min(initial=0.0), ys.max(initial=0.0)
    x_range = (x_max - x_min) or 1.0
    y_range = (y_max - y_min) or 1.0

    degrees = dict(graph.degree())
    max_degree = max(degrees.values(), default=1)

    # network-level scalar
    total_edges = graph.number_of_edges()
    network_density = float(total_edges) / float(max(1, n_nodes * (n_nodes - 1)))
    
    # normalizar length promedio para el embedding
    all_lengths = [feat["length"] for feat in edge_features.values()]
    length_max = max(all_lengths) if all_lengths else 1.0

    embeddings: Dict[str, np.ndarray] = {}
    for idx, (node, data) in enumerate(nodes):
        # características estructurales del nodo
        x = (float(data.get("x", 0.0)) - x_min) / x_range
        y = (float(data.get("y", 0.0)) - y_min) / y_range
        deg = degrees.get(node, 0)
        deg_norm = deg / max_degree if max_degree > 0 else 0.0

        # directed measures if available
        in_deg = graph.in_degree(node) if hasattr(graph, "in_degree") else graph.degree(node)
        out_deg = graph.out_degree(node) if hasattr(graph, "out_degree") else graph.degree(node)

        neighbors = list(graph.neighbors(node))
        neighbor_count = len(neighbors)
        neighbor_degs = [degrees.get(n, 0) for n in neighbors] if neighbors else [0]
        avg_neighbor_deg = float(np.mean(neighbor_degs)) if neighbor_degs else 0.0
        max_neighbor_deg = float(np.max(neighbor_degs)) if neighbor_degs else 0.0
        min_neighbor_deg = float(np.min(neighbor_degs)) if neighbor_degs else 0.0
        neighbor_deg_std = float(np.std(neighbor_degs)) if neighbor_degs else 0.0

        degree_centrality = deg / (n_nodes - 1) if n_nodes > 1 else 0.0
        betweenness_approx = neighbor_count / n_nodes if n_nodes > 0 else 0.0
        
        # características de edges incidentes (promediadas)
        edge_features_node = []
        for u, v, key in graph.edges(node, keys=True):
            feat_key = (u, v, key) if (u, v, key) in edge_features else (v, u, key)
            if feat_key in edge_features:
                edge_features_node.append(edge_features[feat_key])
        
        if edge_features_node:
            length_avg = np.mean([f["length"] for f in edge_features_node]) / length_max
            maxspeed_norm_avg = np.mean([f["maxspeed_norm"] for f in edge_features_node])
            lanes_norm_avg = np.mean([f["lanes_norm"] for f in edge_features_node])
            highway_code_avg = np.mean([f["highway_code"] for f in edge_features_node])
            surface_score_avg = np.mean([f["surface_score"] for f in edge_features_node])
            oneway_flag_avg = np.mean([f["oneway_flag"] for f in edge_features_node])
            travel_time_norm_avg = np.mean([f["travel_time_norm"] for f in edge_features_node])
        else:
            length_avg = 0.0
            maxspeed_norm_avg = 0.0
            lanes_norm_avg = 0.0
            highway_code_avg = 0.0
            surface_score_avg = 0.0
            oneway_flag_avg = 0.0
            travel_time_norm_avg = 0.0
        
        # características de contexto
        intersection_density = _calculate_intersection_density(node, graph)
        road_hierarchy = _calculate_road_hierarchy(node, graph)

        vec = np.array(
            [
                # estructurales (13 features)
                x, y, deg_norm, float(in_deg), float(out_deg),
                float(neighbor_count), avg_neighbor_deg, max_neighbor_deg,
                min_neighbor_deg, neighbor_deg_std, degree_centrality,
                betweenness_approx, network_density,
                # edge features promediadas (7 features)
                length_avg, maxspeed_norm_avg, lanes_norm_avg,
                highway_code_avg, surface_score_avg, oneway_flag_avg,
                travel_time_norm_avg,
                # contexto (2 features)
                intersection_density, road_hierarchy,
            ],
            dtype=np.float32,
        )

        embeddings[str(node)] = vec

    return embeddings
