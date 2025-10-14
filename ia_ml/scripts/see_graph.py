#!/usr/bin/env python3
"""
Script simple para ver el grafo relabel.
"""

import sys
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.download_graph import get_graph_relabel

def main():
    print("Descargando grafo de Río Cuarto...")
    
    # obtener grafo relabel
    G, node_to_idx, idx_to_node = get_graph_relabel("Río Cuarto, Córdoba, Argentina")
    
    print(f"Grafo con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas")
    print(f"Primeros 10 nodos: {list(G.nodes())[:10]}")
    print(f"Primeros 10 aristas: {list(G.edges())[:10]}")
    
    # crear visualización simple
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # dibujar el grafo
    nx.draw(G, pos, 
            node_size=50, 
            node_color='lightblue',
            edge_color='gray',
            with_labels=False,
            alpha=0.7)
    
    plt.title(f"Grafo de Río Cuarto - {G.number_of_nodes()} nodos")
    plt.axis('off')
    plt.tight_layout()
    
    # guardar imagen
    plt.savefig('grafo_rio_cuarto.png', dpi=150, bbox_inches='tight')
    print(f"\nGrafo guardado como 'grafo_rio_cuarto.png'")

    
if __name__ == "__main__":
    main()
