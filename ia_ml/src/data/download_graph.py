import os
import osmnx as ox
import networkx as nx 


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

def get_graph_relabel(locality: str, *, return_original: bool = False):

    safe_name = locality.replace(",", "").replace(" ", "_")
    graph_path = f"ia_ml/src/data/{safe_name}.graphml"

    if not os.path.exists(graph_path):
        G = download_and_save_graph(locality, graph_path)
    else:
        G = load_graph_from_graphml(graph_path)

    G_relabel, node_to_idx, idx_to_node = relabel_nodes_to_indices(G)
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

