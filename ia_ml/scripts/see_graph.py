#!/usr/bin/env python3
"""
Script simple para ver el grafo relabel.
"""

import os
import sys
from pathlib import Path

IA_ML_DIR = str(Path(__file__).parent.parent.resolve()) 
if IA_ML_DIR not in sys.path:
    sys.path.insert(0, IA_ML_DIR)

import networkx as nx
import matplotlib.pyplot as plt
from src.data.download_graph import (
    download_and_save_graph,
    load_graph_from_graphml,
    relabel_nodes_to_indices,
)

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = (SCRIPT_DIR.parent / "data").resolve()
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    print("Descargando grafo de Río Cuarto...")
    locality = "Río Cuarto, Córdoba, Argentina"
    safe_name = locality.replace(",", "").replace(" ", "_")
    graph_filename = f"{safe_name}.graphml"
    graph_path = os.path.join(DATA_DIR, graph_filename)

    if not os.path.exists(graph_path):
        G = download_and_save_graph(locality, graph_path)
    else:
        G = load_graph_from_graphml(graph_path)

    # Relabel usando las utilidades del módulo (evitar llamadas que creen rutas relativas)
    G, node_to_idx, idx_to_node = relabel_nodes_to_indices(G)

    print(f"Grafo con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas")
    print(f"Primeros 10 nodos: {list(G.nodes())[:10]}")
    print(f"Primeros 10 aristas: {list(G.edges())[:10]}")

    # crear visualización simple
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1, iterations=50)

    # dibujar el grafo
    nx.draw(
        G,
        pos,
        node_size=50,
        node_color="lightblue",
        edge_color="gray",
        with_labels=False,
        alpha=0.7,
    )

    plt.title(f"Grafo de Río Cuarto - {G.number_of_nodes()} nodos")
    plt.axis("off")
    plt.tight_layout()

    # guardar imagen en la carpeta DATA_DIR
    out_image = os.path.join(DATA_DIR, "grafo_rio_cuarto.png")
    plt.savefig(out_image, dpi=150, bbox_inches="tight")
    print(f"\nGrafo guardado como '{out_image}'")


if __name__ == "__main__":
    main()