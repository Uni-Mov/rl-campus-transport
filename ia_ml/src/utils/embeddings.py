import numpy as np
import networkx as nx
from typing import Dict

def build_node_embeddings(graph: nx.MultiDiGraph) -> Dict[str, np.ndarray]:
    """Genera embeddings ampliados por nodo:
    [x_norm, y_norm, deg_norm, in_deg, out_deg, neighbor_count,
     avg_neighbor_deg, max_neighbor_deg, min_neighbor_deg, neighbor_deg_std,
     degree_centrality, betweenness_approx, network_density]
    """
    if graph.number_of_nodes() == 0:
        return {}

    nodes = list(graph.nodes(data=True))
    n_nodes = graph.number_of_nodes()

    xs = np.array([float(data.get("x", 0.0)) for _, data in nodes], dtype=np.float32)
    ys = np.array([float(data.get("y", 0.0)) for _, data in nodes], dtype=np.float32)

    x_min, x_max = xs.min(initial=0.0), xs.max(initial=0.0)
    y_min, y_max = ys.min(initial=0.0), ys.max(initial=0.0)
    x_range = (x_max - x_min) or 1.0
    y_range = (y_max - y_min) or 1.0

    degrees = dict(graph.degree())
    max_degree = max(degrees.values(), default=1)

    # Network-level scalar
    total_edges = graph.number_of_edges()
    network_density = float(total_edges) / float(max(1, n_nodes * (n_nodes - 1)))

    embeddings: Dict[str, np.ndarray] = {}
    for idx, (node, data) in enumerate(nodes):
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

        vec = np.array(
            [
                x,
                y,
                deg_norm,
                float(in_deg),
                float(out_deg),
                float(neighbor_count),
                avg_neighbor_deg,
                max_neighbor_deg,
                min_neighbor_deg,
                neighbor_deg_std,
                degree_centrality,
                betweenness_approx,
                network_density,
            ],
            dtype=np.float32,
        )

        embeddings[str(node)] = vec

    return embeddings