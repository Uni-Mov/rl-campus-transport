import os
import osmnx as ox
import networkx as nx
from ia_ml.src.envs.waypoint_navigation import WaypointNavigationEnv 


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

def example_create_env(place="Río Cuarto, Córdoba, Argentina"):
    """Example of creating the WaypointNavigationEnv."""
    graph_path = "ia_ml/src/data/grafo_rio_cuarto.graphml"
    if not os.path.exists(graph_path):
        print("Descargando grafo...")
        G = download_and_save_graph(place, graph_path)
    else:
        print("Cargando grafo desde GraphML...")
        G = load_graph_from_graphml(graph_path)

    G_idx, node_to_idx, idx_to_node = relabel_nodes_to_indices(G)

    n_nodes = G_idx.number_of_nodes()
    if n_nodes < 3:
        raise RuntimeError("Grafo demasiado chico para ejemplo")
    waypoints = [0, max(1, n_nodes // 2)]
    destination = n_nodes - 1

    env = WaypointNavigationEnv(G_idx, waypoints, destination)
    obs, info = env.reset()
    print("obs:", obs, "info:", info)
    return env, node_to_idx, idx_to_node

if __name__ == "__main__":
    example_create_env()