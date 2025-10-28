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
