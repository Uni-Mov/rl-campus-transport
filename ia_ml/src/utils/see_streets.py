from pathlib import Path
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

GRAPH_PATH = Path("ia_ml/src/data/grafo_rio_cuarto.graphml")
SAMPLE_N = 20  # cuántos nodos mostrar (o None para todos)

def load_graph(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"GraphML not found: {path}")
    return ox.load_graphml(str(path))

def street_names_for_node(G, nid):
    """Devuelve una lista única de nombres de vías incidentes al nodo."""
    names = set()
    # G.edges(nid, data=True, keys=True) para MultiGraph con keys
    for u, v, k, attrs in G.edges(nid, keys=True, data=True):
        name = attrs.get("name")
        if not name:
            continue
        # name puede ser str o lista; normalizar
        if isinstance(name, list):
            for n in name:
                names.add(n)
        elif isinstance(name, str):
            # OSM a veces usa ';' para múltiples nombres
            for part in name.split(";"):
                names.add(part.strip())
    return sorted(names)

def reverse_geocode(lat, lon, geolocator, rate_limiter):
    """Intenta obtener la dirección (road, house_number) usando Nominatim."""
    try:
        resp = rate_limiter((lat, lon), addressdetails=True)
        if resp is None:
            return {}
        addr = resp.raw.get("address", {})
        return {
            "road": addr.get("road") or addr.get("pedestrian") or addr.get("residential"),
            "house_number": addr.get("house_number"),
            "display_name": resp.address
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    G = load_graph(GRAPH_PATH)
    nodes = list(G.nodes(data=True))
    total = len(nodes)
    print(f"Graph loaded: nodes={total}, edges={G.number_of_edges()}\n")

    # configurar geocoder (respeta políticas: user_agent y rate limiting)
    geolocator = Nominatim(user_agent="rl-campus-transport-utility")
    rate_limiter = RateLimiter(geolocator.reverse, min_delay_seconds=1.0, max_retries=2)

    sample = nodes if SAMPLE_N is None else nodes[:min(SAMPLE_N, total)]
    for nid, attrs in sample:
        lat = attrs.get("y")
        lon = attrs.get("x")
        names = street_names_for_node(G, nid)
        geo = reverse_geocode(lat, lon, geolocator, rate_limiter)
        print(f"Node {nid}")
        print(f"  coords: lat={lat}, lon={lon}")
        print(f"  street names (from edges): {names or 'N/A'}")
        if geo.get("error"):
            print(f"  reverse-geocode error: {geo['error']}")
        else:
            print(f"  reverse geocode road: {geo.get('road')}, house_number: {geo.get('house_number')}")
        print("-" * 60)

if __name__ == "__main__":
    main()