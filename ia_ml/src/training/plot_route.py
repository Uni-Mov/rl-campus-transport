"""Genera mapas del recorrido del agente y rutas de referencia usando OSMnx."""

from __future__ import annotations

import argparse
import ast
import os
import sys
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

# Habilitar imports relativos cuando se ejecuta como script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data.download_graph import get_graph_relabel, indices_to_osm_nodes 
from src.training.run_inference import run_episode  


def parse_path(path_str: str) -> List[int]:
    try:
        candidate = ast.literal_eval(path_str)
    except (SyntaxError, ValueError) as exc:
        raise argparse.ArgumentTypeError("El camino debe ser una lista de enteros.") from exc
    if not isinstance(candidate, (list, tuple)):
        raise argparse.ArgumentTypeError("El camino debe ser una lista de enteros.")
    try:
        return [int(x) for x in candidate]
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("El camino contiene valores no enteros.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plotea recorridos del agente y rutas OSMnx.")
    parser.add_argument("--place", type=str, required=True, help="Localidad usada para descargar el grafo")
    parser.add_argument(
        "--path",
        type=parse_path,
        default=None,
        help="Camino en índices (ej. '[0,1,2]'). Si se omite, se ejecuta el modelo para obtenerlo.",
    )
    parser.add_argument("--model-path", type=str, default=None, help="Modelo .zip para inferencia si no hay --path")
    parser.add_argument("--output", type=str, default="route.png", help="Ruta base del archivo de salida")
    parser.add_argument("--plot-graph", action="store_true", help="Dibujar también el grafo completo de fondo")
    parser.add_argument("--start", type=int, default=0, help="Índice del nodo inicial")
    parser.add_argument("--destination", type=int, default=-1, help="Índice del nodo destino (por defecto último nodo)")
    parser.add_argument("--waypoints", type=int, nargs="*", default=[], help="Índices de waypoints a resaltar")
    parser.add_argument("--max-steps", type=int, default=None, help="Pasos máximos al ejecutar el modelo")
    parser.add_argument("--deterministic", action="store_true", help="Usar política determinística en inferencia")
    parser.add_argument("--verbose", action="store_true", help="Mostrar logs durante inferencia")
    parser.add_argument("--osm-route", action="store_true", help="Generar sólo la ruta OSMnx más corta")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Generar rutas del modelo y OSMnx, y comparar sus distancias",
    )
    return parser.parse_args()


def compute_osm_route(G_osm: nx.MultiDiGraph, node_sequence: List[int]) -> List[int]:
    route: List[int] = []
    for u, v in zip(node_sequence, node_sequence[1:]):
        try:
            segment = nx.shortest_path(G_osm, u, v, weight="travel_time")
        except (nx.NetworkXNoPath, nx.NetworkXError):
            segment = nx.shortest_path(G_osm, u, v, weight="length")
        if route:
            route.extend(segment[1:])
        else:
            route.extend(segment)
    return route


def _edge_attr_list(edge_data: object) -> List[Dict[str, float]]:
    if not isinstance(edge_data, dict):
        return []
    if all(isinstance(val, dict) for val in edge_data.values()):
        return [attrs for attrs in edge_data.values()]
    return [edge_data]


def compute_path_metrics(G_osm: nx.MultiDiGraph, path_nodes: List[int]) -> Tuple[float, float]:
    travel_total = 0.0
    length_total = 0.0
    for u, v in zip(path_nodes, path_nodes[1:]):
        attrs_list = _edge_attr_list(G_osm.get_edge_data(u, v, default={}))
        if not attrs_list:
            try:
                travel = float(nx.shortest_path_length(G_osm, u, v, weight="travel_time"))
            except (nx.NetworkXNoPath, nx.NetworkXError):
                travel = float(nx.shortest_path_length(G_osm, u, v, weight="length"))
            length = travel
        else:
            travel_candidates = [float(attr["travel_time"]) for attr in attrs_list if "travel_time" in attr]
            length_candidates = [float(attr["length"]) for attr in attrs_list if "length" in attr]
            travel = min(travel_candidates) if travel_candidates else None
            length = min(length_candidates) if length_candidates else None
            if travel is None and length is not None:
                travel = length
            if length is None and travel is not None:
                length = travel
            if travel is None:
                travel = 0.0
            if length is None:
                length = 0.0
        travel_total += travel
        length_total += length
    return travel_total, length_total


def ensure_extension(path: str, default_ext: str = ".png") -> Tuple[str, str]:
    base, ext = os.path.splitext(path)
    if not ext:
        ext = default_ext
    return base, ext


def plot_route_image(
    G_osm: nx.MultiDiGraph,
    path_nodes: List[int],
    idx_to_node: Dict[int, int],
    start_idx: Optional[int],
    dest_idx: Optional[int],
    waypoint_indices: List[int],
    output_path: str,
    plot_graph: bool,
) -> None:
    if len(path_nodes) < 2:
        raise RuntimeError("El camino debe contener al menos dos nodos para graficar.")

    fig, ax = ox.plot_graph_route(
        G_osm,
        path_nodes,
        node_size=0,
        route_color="red",
        route_linewidth=3,
        bgcolor="white",
        show=False,
        close=False,
    )

    if plot_graph:
        ox.plot_graph(G_osm, ax=ax, node_size=0, edge_color="#cccccc", show=False, close=False)

    def to_nodes(indices: List[int]) -> List[int]:
        return indices_to_osm_nodes(indices, idx_to_node)

    start_nodes = to_nodes([start_idx]) if start_idx is not None else []
    dest_nodes = to_nodes([dest_idx]) if dest_idx is not None else []
    waypoint_nodes = to_nodes(waypoint_indices) if waypoint_indices else []

    if not start_nodes:
        start_nodes = path_nodes[:1]
    if not dest_nodes:
        dest_nodes = path_nodes[-1:]

    def scatter(nodes: List[int], *, color: str, marker: str, label: Optional[str], size: int) -> None:
        if not nodes:
            return
        xs = [G_osm.nodes[n]["x"] for n in nodes if n in G_osm.nodes]
        ys = [G_osm.nodes[n]["y"] for n in nodes if n in G_osm.nodes]
        if xs and ys:
            ax.scatter(xs, ys, c=color, s=size, marker=marker, edgecolors="black", linewidths=0.5, label=label)

    scatter(start_nodes, color="lime", marker="^", label="Inicio", size=60)
    scatter(dest_nodes, color="gold", marker="s", label="Destino", size=60)
    scatter(waypoint_nodes, color="dodgerblue", marker="o", label="Waypoints", size=40)

    if start_nodes or dest_nodes or waypoint_nodes:
        ax.legend(loc="best")

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Mapa guardado en {output_path}")


def validate_indices(indices: List[int], idx_to_node: Dict[int, int], label: str) -> None:
    missing = [idx for idx in indices if idx not in idx_to_node]
    if missing:
        raise ValueError(f"{label} inexistentes en el grafo: {missing}")


def convert_indices(path_indices: List[int], mapping: Dict[int, int]) -> List[int]:
    osm_nodes = indices_to_osm_nodes(path_indices, mapping)
    if len(osm_nodes) < 2:
        raise RuntimeError("El camino debe contener al menos dos nodos convertibles a OSM.")
    return osm_nodes


def report_metrics(label: str, travel_time: float, length: float) -> None:
    km = length / 1000.0
    print(f"  {label:<12} -> travel_time ≈ {travel_time:.1f} s, distancia ≈ {km:.3f} km")


def main() -> None:
    args = parse_args()

    _, node_to_idx, idx_to_node, G_osm = get_graph_relabel(args.place, return_original=True)

    base_start_idx = args.start
    base_dest_idx = args.destination if args.destination not in (None, -1) else max(idx_to_node.keys())

    if base_start_idx not in idx_to_node:
        raise ValueError(f"Índice de inicio {base_start_idx} no pertenece al grafo")
    validate_indices(list(args.waypoints), idx_to_node, "Waypoints")
    if base_dest_idx not in idx_to_node:
        raise ValueError(f"Índice de destino {base_dest_idx} no pertenece al grafo")

    if args.compare:
        if not args.model_path:
            raise ValueError("--compare requiere proporcionar --model-path")

        rl_result = run_episode(
            place=args.place,
            model_path=args.model_path,
            start=base_start_idx,
            waypoints=args.waypoints,
            destination=base_dest_idx,
            max_steps=args.max_steps,
            deterministic=args.deterministic,
            verbose=args.verbose,
        )
        rl_indices = rl_result["path"]
        if len(rl_indices) < 2:
            raise RuntimeError("El modelo no devolvió un camino válido para graficar")
        rl_osm_nodes = convert_indices(rl_indices, rl_result["idx_to_node"])
        rl_metrics = compute_path_metrics(G_osm, rl_osm_nodes)

        seq_indices = [base_start_idx, *args.waypoints, base_dest_idx]
        seq_osm = convert_indices(seq_indices, idx_to_node)
        osm_nodes = compute_osm_route(G_osm, seq_osm)
        osm_metrics = compute_path_metrics(G_osm, osm_nodes)

        base, ext = ensure_extension(args.output)
        rl_output = f"{base}_rl{ext}"
        osm_output = f"{base}_osm{ext}"

        plot_route_image(
            G_osm,
            rl_osm_nodes,
            idx_to_node,
            base_start_idx,
            base_dest_idx,
            args.waypoints,
            rl_output,
            args.plot_graph,
        )
        plot_route_image(
            G_osm,
            osm_nodes,
            idx_to_node,
            base_start_idx,
            base_dest_idx,
            args.waypoints,
            osm_output,
            args.plot_graph,
        )

        print("\nDistancias aproximadas")
        print("=======================")
        report_metrics("Modelo RL", *rl_metrics)
        report_metrics("OSMnx", *osm_metrics)
        diff = rl_metrics[1] - osm_metrics[1]
        print(f"  Diferencia   -> {diff/1000.0:.3f} km (RL - OSMnx)")
        return

    if args.osm_route:
        seq_indices = [base_start_idx, *args.waypoints, base_dest_idx]
        seq_osm = convert_indices(seq_indices, idx_to_node)
        osm_nodes = compute_osm_route(G_osm, seq_osm)
        metrics = compute_path_metrics(G_osm, osm_nodes)
        base, ext = ensure_extension(args.output)
        output_path = f"{base}{ext}"
        plot_route_image(
            G_osm,
            osm_nodes,
            idx_to_node,
            base_start_idx,
            base_dest_idx,
            args.waypoints,
            output_path,
            args.plot_graph,
        )
        print("\nDistancias aproximadas")
        report_metrics("OSMnx", *metrics)
        return

    if args.path is None:
        if not args.model_path:
            raise ValueError("Debes proporcionar --model-path o un --path explícito")
        rl_result = run_episode(
            place=args.place,
            model_path=args.model_path,
            start=base_start_idx,
            waypoints=args.waypoints,
            destination=base_dest_idx,
            max_steps=args.max_steps,
            deterministic=args.deterministic,
            verbose=args.verbose,
        )
        path_indices = rl_result["path"]
        if len(path_indices) < 2:
            raise RuntimeError("El modelo no devolvió un camino válido para graficar")
        mapping_for_path = rl_result["idx_to_node"]
    else:
        path_indices = args.path
        mapping_for_path = idx_to_node

    path_nodes = convert_indices(path_indices, mapping_for_path)
    metrics = compute_path_metrics(G_osm, path_nodes)
    base, ext = ensure_extension(args.output)
    output_path = f"{base}{ext}"
    plot_route_image(
        G_osm,
        path_nodes,
        idx_to_node,
        base_start_idx,
        base_dest_idx,
        args.waypoints,
        output_path,
        args.plot_graph,
    )
    print("\nDistancias aproximadas")
    report_metrics("Ruta", *metrics)


if __name__ == "__main__":
    main()
