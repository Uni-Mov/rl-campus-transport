import pytest
import osmnx as ox

@pytest.fixture(scope="session")
def city_graph():
    """Descarga y devuelve el grafo de una ciudad"""
    graph = ox.graph_from_place("Río Cuarto, Córdoba, Argentina", network_type="drive")
    return graph