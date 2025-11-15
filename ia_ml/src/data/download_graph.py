import os
import osmnx as ox
import networkx as nx 
import pickle
from typing import Dict, Optional


def _configure_osmnx():
    """Configures OSMnx to use cache and not log to console."""
    try:
        ox.config(use_cache=True, log_console=False)
    except AttributeError:
        try:
            ox.settings.use_cache = True
            ox.settings.log_console = False
        except Exception:
            pass

def download_and_save_graph(place_name: str, out_path: str):
    """Download road network (drive) and save to GraphML."""
    _configure_osmnx()
    G = ox.graph_from_place(place_name, network_type="drive")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ox.save_graphml(G, out_path)
    return G

def load_graph_from_graphml(path: str) -> nx.MultiDiGraph:
    """Load a graph saved as GraphML (OSMnx format)."""
    G = ox.load_graphml(path)
    return G

def relabel_nodes_to_indices(G: nx.Graph):
    """Relabel nodes to 0..n-1 and return (G_relabel, node_to_idx, idx_to_node)."""
    nodes = list(G.nodes())
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}
    idx_to_node = {idx: node for node, idx in node_to_idx.items()}
    G_relabeled = nx.relabel_nodes(G, node_to_idx, copy=True)
    return G_relabeled, node_to_idx, idx_to_node

def precompute_and_save_distances(G: nx.Graph, out_path: str, weight: str = "length") -> Dict:
    """Compute all-pairs shortest path lengths and save to out_path (pickle)."""
    print(f"[INFO] Precomputing all-pairs shortest path lengths (weight={weight}) ...")
    lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight=weight))
    with open(out_path, "wb") as fh:
        pickle.dump(lengths, fh, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[INFO] Distances saved to {out_path}")
    return lengths

def load_distances_if_present(path: str) -> Optional[Dict]:
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None

def get_graph_relabel(locality: str, *, return_original: bool = False):
    safe_name = locality.replace(",", "").replace(" ", "_")
    graph_path = f"ia_ml/src/data/{safe_name}.graphml"
    distances_path = f"ia_ml/src/data/{safe_name}_distances.pkl"

    if not os.path.exists(graph_path):
        G = download_and_save_graph(locality, graph_path)
    else:
        G = load_graph_from_graphml(graph_path)

    # Try load distances if present; attach to original graph (OSM IDs)
    distances = load_distances_if_present(distances_path)
    if distances is not None:
        G.graph["distances"] = distances

    G_relabel, node_to_idx, idx_to_node = relabel_nodes_to_indices(G)
    # If distances exist on original, convert to relabeled ids for faster lookup
    if "distances" in G.graph:
        # Convert keys from original OSM node ids to relabeled indices
        converted = {}
        for orig_u, dist_dict in G.graph["distances"].items():
            u_idx = node_to_idx.get(orig_u)
            if u_idx is None:
                continue
            converted[u_idx] = {}
            for orig_v, d in dist_dict.items():
                v_idx = node_to_idx.get(orig_v)
                if v_idx is None:
                    continue
                converted[u_idx][v_idx] = float(d)
        G_relabel.graph["distances"] = converted

    if return_original:
        return G_relabel, node_to_idx, idx_to_node, G
    return G_relabel, node_to_idx, idx_to_node


def indices_to_osm_nodes(path_indices, idx_to_node):
    """Convierte un camino en índices (0..n-1) a IDs originales de OSM."""
    converted = []
    for idx in path_indices:
        try:
            converted.append(idx_to_node[int(idx)])
        except (KeyError, ValueError, TypeError):
            continue
    return converted

def load_subgraph_from_file(graphml_path: str):
    """Carga un subgrafo desde un archivo .graphml y lo relabela a índices.
    
    Args:
        graphml_path: Ruta al archivo .graphml
        
    Returns:
        Tuple[G_relabeled, node_to_idx, idx_to_node]
    """
    G = load_graph_from_graphml(graphml_path)
    
    # Intentar cargar distancias si existen (mismo nombre pero .pkl)
    distances_path = graphml_path.replace('.graphml', '_distances.pkl')
    distances = load_distances_if_present(distances_path)
    if distances is not None:
        G.graph["distances"] = distances
    
    G_relabel, node_to_idx, idx_to_node = relabel_nodes_to_indices(G)
    
    # Convertir distancias de IDs originales a índices relabeled
    if "distances" in G.graph:
        converted = {}
        for orig_u, dist_dict in G.graph["distances"].items():
            u_idx = node_to_idx.get(orig_u)
            if u_idx is None:
                continue
            converted[u_idx] = {}
            for orig_v, d in dist_dict.items():
                v_idx = node_to_idx.get(orig_v)
                if v_idx is None:
                    continue
                converted[u_idx][v_idx] = float(d)
        G_relabel.graph["distances"] = converted
    
    return G_relabel, node_to_idx, idx_to_node

