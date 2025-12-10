#!/usr/bin/env python3
"""
Script simplificado para extraer un subgrafo desde una localidad.

Descarga/carga el grafo de la localidad, calcula su centro automáticamente,
y extrae un subgrafo con el radio especificado.

Uso:
    python scripts/get_subgraph.py --locality "Río Cuarto, Córdoba, Argentina" \
                                   --radius 1000 \
                                   --output subgraph.graphml
"""
import os
import sys
from pathlib import Path
import argparse
import osmnx as ox
import networkx as nx
import math
import numpy as np
import matplotlib.pyplot as plt

IA_ML_DIR = str(Path(__file__).parent.parent.resolve())
if IA_ML_DIR not in sys.path:
    sys.path.insert(0, IA_ML_DIR)

def load_graph_with_radius(locality: str, radius_meters: float) -> nx.MultiDiGraph:
    """Descarga la red vial centrada en la localidad con un radio dado.

    Esto usa el centro geocodificado de la localidad y `graph_from_point` con
    `dist=radius_meters`, por lo que incluye localidades aledañas si el radio
    supera el área administrativa (ej: 10 km incluye Higueras y alrededores).
    """
    # Silenciar logs y reutilizar cache de OSMnx
    try:
        ox.config(use_cache=True, log_console=False)
    except AttributeError:
        try:
            ox.settings.use_cache = True
            ox.settings.log_console = False
        except Exception:
            pass

    # Geocodificar y descargar grafo por radio
    center_lat, center_lon = ox.geocode(locality)
    return ox.graph_from_point(
        (center_lat, center_lon),
        dist=radius_meters,
        network_type="drive",
    )


def calculate_graph_center(graph: nx.MultiDiGraph) -> tuple:
    """Calcula el centro geográfico del grafo (promedio de coordenadas de nodos)."""
    lons = []
    lats = []
    
    for node, data in graph.nodes(data=True):
        x = data.get("x")  # longitud
        y = data.get("y")  # latitud
        if x is not None and y is not None:
            lons.append(float(x))
            lats.append(float(y))
    
    if not lons or not lats:
        raise ValueError("El grafo no tiene coordenadas geográficas en los nodos")
    
    center_lon = np.mean(lons)
    center_lat = np.mean(lats)
    
    return center_lat, center_lon


def extract_by_center_point(
    graph: nx.MultiDiGraph,
    center_lat: float,
    center_lon: float,
    distance_meters: float
) -> nx.MultiDiGraph:
    """Extrae subgrafo alrededor de un punto central dentro de una distancia."""
    # Convertir distancia en metros a grados aproximados
    # 1 grado latitud ≈ 111 km
    lat_deg_per_m = 1.0 / 111000.0
    lon_deg_per_m = 1.0 / (111000.0 * abs(math.cos(math.radians(center_lat))))
    
    # Calcular bounding box
    north = center_lat + (distance_meters * lat_deg_per_m)
    south = center_lat - (distance_meters * lat_deg_per_m)
    east = center_lon + (distance_meters * lon_deg_per_m)
    west = center_lon - (distance_meters * lon_deg_per_m)
    
    # Extraer nodos dentro del bounding box
    subgraph_nodes = []
    for node, data in graph.nodes(data=True):
        x = data.get("x")  # longitud
        y = data.get("y")  # latitud
        if x is not None and y is not None:
            if west <= x <= east and south <= y <= north:
                subgraph_nodes.append(node)
    
    if not subgraph_nodes:
        raise ValueError(f"No se encontraron nodos dentro del radio de {distance_meters}m desde ({center_lat}, {center_lon})")
    
    subgraph = graph.subgraph(subgraph_nodes).copy()
    
    # Mantener solo la componente conexa más grande para evitar islas
    if subgraph.is_directed():
        components = list(nx.strongly_connected_components(subgraph))
    else:
        components = list(nx.connected_components(subgraph.to_undirected()))
    
    if components:
        largest_component = max(components, key=len)
        subgraph = subgraph.subgraph(largest_component).copy()
    
    return subgraph


def main():
    parser = argparse.ArgumentParser(
        description="Extrae un subgrafo desde una localidad (descarga/carga automáticamente)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/get_subgraph.py --locality "Río Cuarto, Córdoba, Argentina" --radius 1000 --output subgraph.graphml
  python scripts/get_subgraph.py --locality "Guatimozin, Cordoba, Argentina" --radius 500 --output subgraph.graphml --visualize
  python scripts/get_subgraph.py --locality "Río Cuarto, Córdoba, Argentina" --radius 1000 --output subgraph.graphml --save-plot subgraph.png
        """
    )
    
    parser.add_argument(
        "--locality", "-l",
        type=str,
        required=True,
        help="Nombre de la localidad (ej: 'Río Cuarto, Córdoba, Argentina')"
    )
    
    parser.add_argument(
        "--radius", "-r",
        type=float,
        required=True,
        metavar="METERS",
        help="Radio en metros desde el centro del grafo"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Ruta donde guardar el subgrafo (formato GraphML)"
    )
    
    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Mostrar visualización del subgrafo"
    )
    
    parser.add_argument(
        "--save-plot",
        type=str,
        help="Guardar visualización en archivo (ej: subgraph.png)"
    )
    
    args = parser.parse_args()
    
    # Descargar grafo usando radio para incluir localidades cercanas (e.g., Higueras)
    print(f" Cargando/descargando grafo por radio {args.radius} m desde: {args.locality}")
    graph = load_graph_with_radius(args.locality, args.radius)

    print(f"Grafo descargado: {graph.number_of_nodes()} nodos, {graph.number_of_edges()} edges")
    
    # Calcular centro del grafo
    print(f" Calculando centro geográfico del grafo...")
    try:
        center_lat, center_lon = calculate_graph_center(graph)
        print(f" Centro calculado: ({center_lat:.6f}, {center_lon:.6f})")
    except ValueError as e:
        print(f" {e}")
        sys.exit(1)
    
    # Extraer subgrafo
    print(f" Extrayendo subgrafo con radio de {args.radius} metros...")
    try:
        subgraph = extract_by_center_point(graph, center_lat, center_lon, args.radius)
        print(f" Subgrafo extraído: {subgraph.number_of_nodes()} nodos, {subgraph.number_of_edges()} edges")
    except ValueError as e:
        print(f" {e}")
        sys.exit(1)
    
    # Guardar subgrafo en la carpeta del script
    script_dir = Path(__file__).parent
    output_path = script_dir / args.output
    
    print(f" Guardando subgrafo en: {output_path}")
    ox.save_graphml(subgraph, str(output_path))
    print(f"Subgrafo guardado exitosamente")
    print(f"     Nodos: {subgraph.number_of_nodes()}")
    print(f"     Edges: {subgraph.number_of_edges()}")
    
    # visualizar subgrafo si se solicita
    if args.visualize or args.save_plot:
        print(f" Generando visualización del subgrafo...")
        try:
            fig, ax = ox.plot_graph(
                subgraph,
                node_size=20,
                node_color='red',
                edge_color='gray',
                edge_linewidth=0.5,
                show=False,
                close=False
            )
            
            if args.save_plot:
                plot_path = script_dir / args.save_plot
                fig.savefig(str(plot_path), dpi=150, bbox_inches='tight')
                print(f" Visualización guardada en: {plot_path}")
            
            if args.visualize:
                plt.show()
            else:
                plt.close(fig)
        except Exception as e:
            print(f" Error al visualizar: {e}")
            print(f" (puede que falten dependencias de visualización)")


if __name__ == "__main__":
    main()

