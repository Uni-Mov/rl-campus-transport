import os
import pickle
import networkx as nx

def precalculate_distances(G, cache_path="data/distances_cache.pkl"):
    """
    Precalcula las distancias más cortas entre todos los nodos de un grafo usando Dijkstra.
    Si existe un archivo cache, lo carga directamente para evitar recalcular.
    
    """

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # Si ya existe un cache previo, lo cargamos
    if os.path.exists(cache_path):
        print(f"[distances] Cargando distancias desde cache: {cache_path}")
        with open(cache_path, "rb") as f:
            shortest_paths = pickle.load(f)
        return shortest_paths

    # Si no existe, las calculamos
    print("[distances] Calculando distancias entre nodos (esto puede tardar)...")
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G))

    # Guardamos en cache para próximas ejecuciones
    with open(cache_path, "wb") as f:
        pickle.dump(shortest_paths, f)

    print(f"[distances] Distancias precalculadas y guardadas en {cache_path}")
    return shortest_paths


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Precompute shortest-path distances for a graphml file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 src/utils/distances.py -g scripts/subgraph.graphml\n"
            "  python3 src/utils/distances.py -g scripts/subgraph.graphml -c src/data/mygraph_distances.pkl\n"
            "\n"
            "Notes:\n"
            "  - The output cache is a pickle of the all-pairs shortest-path lengths.\n"
            "  - For large graphs this can take significant time and memory. Consider computing\n"
            "    only target-based distances if you have many nodes but few targets.\n"
        ),
    )
    parser.add_argument("-g", "--graph", required=True, help="Path to input .graphml file")
    parser.add_argument("-c", "--cache", default="src/data/subgraph_distances.pkl", help="Output cache path (.pkl)")
    args = parser.parse_args()

    graph_path = Path(args.graph)
    if not graph_path.exists():
        raise SystemExit(f"Graph file not found: {graph_path}")

    G = nx.read_graphml(str(graph_path))

    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[distances] Precomputing distances for {graph_path} -> {cache_path} (this may take some time)...")
    precalculate_distances(G, cache_path=str(cache_path))
    print("[distances] Done.")
