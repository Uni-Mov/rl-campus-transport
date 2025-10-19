import numpy as np
import networkx as nx
from typing import Dict

def build_node_embeddings(graph: nx.MultiDiGraph) -> Dict[str, np.ndarray]:
    """Genera embeddings simples (x, y, grado normalizado) para cada nodo del grafo."""
    if graph.number_of_nodes() == 0:
        return {}

    xs = np.array([float(data.get("x", 0.0)) for _, data in graph.nodes(data=True)], dtype=np.float32)
    ys = np.array([float(data.get("y", 0.0)) for _, data in graph.nodes(data=True)], dtype=np.float32)

    x_min, x_max = xs.min(initial=0.0), xs.max(initial=0.0)
    y_min, y_max = ys.min(initial=0.0), ys.max(initial=0.0)

    x_range = (x_max - x_min) or 1.0
    y_range = (y_max - y_min) or 1.0

    degrees = dict(graph.degree())
    max_degree = max(degrees.values(), default=1)

    embeddings = {}
    for node, data in graph.nodes(data=True):
        x = (float(data.get("x", 0.0)) - x_min) / x_range
        y = (float(data.get("y", 0.0)) - y_min) / y_range
        deg = degrees.get(node, 0) / max_degree
        embeddings[str(node)] = np.array([x, y, deg], dtype=np.float32)

    return embeddings
