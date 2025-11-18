import os
from pathlib import Path
import osmnx as ox

GRAPH_PATH = Path("../data/grafo_rio_cuarto.graphml")
SHOW_N = 5  # How many nodes/edges to show

def load_graph(path: Path):
    """Loads the downloaded graph from GraphML."""
    if not path.exists():
        raise FileNotFoundError(f"GraphML not found: {path}")
    return ox.load_graphml(str(path))

def fmt_node(nid, attrs, G):
    """Formats a node's info."""
    lat = attrs.get("y")
    lon = attrs.get("x")
    street_count = attrs.get("street_count")
    deg = G.degree(nid)
    keys = ", ".join(list(attrs.keys()))
    return (f"id: {nid}\n"
            f"   lat: {lat}, lon: {lon}, street_count: {street_count}, degree: {deg}\n"
            f"   attrs: {keys}")

def fmt_edge(u, v, key, attrs):
    """Formats an edge's info."""
    length = attrs.get("length")
    highway = attrs.get("highway")
    lanes = attrs.get("lanes")
    maxspeed = attrs.get("maxspeed")
    oneway = attrs.get("oneway")
    osmid = attrs.get("osmid")
    has_geom = "geometry" in attrs
    return (f"{u} -[{key}]-> {v}\n"
            f"   length(m): {length}, highway: {highway}, lanes: {lanes}, maxspeed: {maxspeed}, oneway: {oneway}, osmid: {osmid}, geometry: {has_geom}")

def show_neighbors_sample(G, nid, max_show=5):
    """Shows a sample of neighbors for a node."""
    neigh = list(G.neighbors(nid))
    lines = []
    for nb in neigh[:max_show]:
        attrs = G.nodes[nb]
        lines.append(f"      {nb} (lat={attrs.get('y')}, lon={attrs.get('x')})")
    more = f"      ... and {len(neigh)-max_show} more" if len(neigh) > max_show else ""
    return "\n".join(lines + ([more] if more else []))

def main():
    """Main function to load graph and display nodes and edges."""
    G = load_graph(GRAPH_PATH)
    print(f"Graph loaded: nodes={G.number_of_nodes()}, edges={G.number_of_edges()}\n")

    nodes = list(G.nodes(data=True))
    print(f"--- Primeros {min(SHOW_N, len(nodes))} NODOS ---")
    for i, (nid, attrs) in enumerate(nodes[:SHOW_N], 1):
        print(f"{i}. {fmt_node(nid, attrs, G)}")
        print("   Neighbors sample:")
        print(show_neighbors_sample(G, nid))
        print()

    edges = list(G.edges(keys=True, data=True))
    print(f"--- Primeras {min(SHOW_N, len(edges))} ARISTAS ---")
    for i, (u, v, k, attrs) in enumerate(edges[:SHOW_N], 1):
        print(f"{i}. {fmt_edge(u, v, k, attrs)}\n")

if __name__ == "__main__":
    main()