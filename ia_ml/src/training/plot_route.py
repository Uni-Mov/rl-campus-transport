"""Genera mapas del recorrido del agente y rutas de referencia usando OSMnx."""

from __future__ import annotations

import argparse
import ast
import os
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import glob

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

# Habilitar imports relativos cuando se ejecuta como script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data.download_graph import get_graph_relabel, indices_to_osm_nodes, load_subgraph_from_file 
from src.training.run_inference import run_episode
from pathlib import Path  


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
    parser = argparse.ArgumentParser(
        description="Plotea recorridos del agente y rutas OSMnx.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

Con localidad (grafo completo):
  python src/training/plot_route.py --place "Río Cuarto, Córdoba, Argentina" --start 0 --destination 100 --model-path logs/best_model.zip --output route.png
  python src/training/plot_route.py --place "Río Cuarto, Córdoba, Argentina" --start 0 --destination 100 --waypoints 10 20 --compare --model-path logs/best_model.zip
  python src/training/plot_route.py --place "Río Cuarto, Córdoba, Argentina" --start 0 --destination 100 --waypoints 10 20 --compare --find-best --model-dir logs/ --verbose
  python src/training/plot_route.py --place "Río Cuarto, Córdoba, Argentina" --start 0 --destination 100 --osm-route --output osm_route.png
  python src/training/plot_route.py --place "Río Cuarto, Córdoba, Argentina" --path "[0,5,10,15,20]" --output custom_path.png

Con subgrafo:
  python src/training/plot_route.py --subgraph scripts/subgraph.graphml --start 0 --destination 50 --model-path logs/best_model.zip --output route_subgraph.png
  python src/training/plot_route.py --subgraph scripts/subgraph.graphml --start 0 --destination 50 --waypoints 10 20 --compare --model-path logs/best_model.zip --output comparison
  python src/training/plot_route.py --subgraph scripts/subgraph.graphml --start 0 --destination 50 --waypoints 10 20 --compare --find-best --model-dir logs/ --verbose
  python src/training/plot_route.py --subgraph scripts/subgraph.graphml --start 0 --destination 50 --osm-route --output osm_subgraph.png
  python src/training/plot_route.py --subgraph scripts/subgraph.graphml --path "[0,5,10,15,20]" --output custom_subgraph.png
        """
    )
    graph_group = parser.add_mutually_exclusive_group(required=True)
    graph_group.add_argument("--place", type=str, help="Localidad usada para descargar el grafo")
    graph_group.add_argument("--subgraph", type=str, help="Ruta al archivo .graphml del subgrafo")
    parser.add_argument(
        "--path",
        type=parse_path,
        default=None,
        help="Camino en índices (ej. '[0,1,2]'). Si se omite, se ejecuta el modelo para obtenerlo.",
    )
    parser.add_argument("--model-path", type=str, default=None, help="Modelo .zip para inferencia si no hay --path")
    parser.add_argument("--model-dir", type=str, default=None, help="Directorio con múltiples modelos .zip para evaluar y seleccionar el mejor")
    parser.add_argument("--find-best", action="store_true", help="Evaluar múltiples modelos y usar el que tenga menor diferencia con OSMnx")
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
    """calcula ruta osm usando shortest_path entre nodos en la secuencia.
    
    los nodos deben ser ids osm originales (no índices relabeled).
    """
    route: List[int] = []
    for u, v in zip(node_sequence, node_sequence[1:]):
        # verificar que los nodos existan en el grafo
        if u not in G_osm or v not in G_osm:
            print(f"[WARNING] nodos {u} o {v} no encontrados en el grafo, saltando segmento")
            continue
        
        try:
            # intentar con travel_time primero
            segment = nx.shortest_path(G_osm, u, v, weight="travel_time")
        except (nx.NetworkXNoPath, nx.NetworkXError):
            try:
                # fallback a length
                segment = nx.shortest_path(G_osm, u, v, weight="length")
            except (nx.NetworkXNoPath, nx.NetworkXError):
                print(f"[WARNING] no se encontró ruta entre {u} y {v}")
                # si no hay ruta, agregar solo el nodo destino
                segment = [v]
        
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


def find_best_model(
    model_dir: Optional[str],
    model_path: Optional[str],
    subgraph_path: Optional[str],
    place: Optional[str],
    start_idx: int,
    destination_idx: int,
    waypoints: List[int],
    idx_to_node: Dict[int, int],
    G_osm: nx.MultiDiGraph,
    max_steps: Optional[int],
    deterministic: bool,
    verbose: bool,
) -> Tuple[str, float]:
    """evalúa múltiples modelos y retorna el que tenga menor diferencia con osm.
    
    returns:
        (best_model_path, best_difference_in_meters)
    """
    # recopilar modelos a evaluar
    models_to_test = []
    
    if model_dir:
        model_dir_path = Path(model_dir)
        if not model_dir_path.exists():
            raise ValueError(f"directorio de modelos no encontrado: {model_dir}")
        models_to_test.extend(list(model_dir_path.glob("*.zip")))
        if verbose:
            print(f"[INFO] encontrados {len(models_to_test)} modelos en {model_dir}")
    
    if model_path:
        model_path_obj = Path(model_path)
        if model_path_obj.is_dir():
            models_to_test.extend(list(model_path_obj.glob("*.zip")))
        elif model_path_obj.exists():
            models_to_test.append(model_path_obj)
        else:
            # buscar en subdirectorios comunes
            for pattern in ["logs/**/*.zip", "**/best_model*.zip", "**/*model*.zip"]:
                found = list(Path(".").glob(pattern))
                if found:
                    models_to_test.extend(found)
                    break
    
    if not models_to_test:
        raise ValueError("no se encontraron modelos para evaluar")
    
    if verbose:
        print(f"[INFO] evaluando {len(models_to_test)} modelos...")
    
    best_model = None
    best_diff = float('inf')
    results = []
    
    # preparar argumentos para run_episode
    episode_base_kwargs = {
        "start": start_idx,
        "waypoints": waypoints,
        "destination": destination_idx,
        "max_steps": max_steps,
        "deterministic": deterministic,
        "verbose": False,  # silenciar durante evaluación
    }
    if subgraph_path:
        episode_base_kwargs["subgraph_path"] = subgraph_path
    else:
        episode_base_kwargs["place"] = place
    
    # convertir índices a nodos osm para calcular ruta óptima
    seq_indices = [start_idx, *waypoints, destination_idx]
    seq_osm = convert_indices(seq_indices, idx_to_node)
    osm_nodes = compute_osm_route(G_osm, seq_osm)
    osm_metrics = compute_path_metrics(G_osm, osm_nodes)
    osm_length = osm_metrics[1]
    
    # evaluar cada modelo
    for model_file in models_to_test:
        try:
            episode_kwargs = episode_base_kwargs.copy()
            episode_kwargs["model_path"] = str(model_file)
            
            rl_result = run_episode(**episode_kwargs)
            rl_indices = rl_result["path"]
            
            if len(rl_indices) < 2:
                if verbose:
                    print(f"[WARNING] modelo {model_file.name} no produjo un camino válido")
                continue
            
            rl_osm_nodes = convert_indices(rl_indices, rl_result["idx_to_node"])
            rl_metrics = compute_path_metrics(G_osm, rl_osm_nodes)
            rl_length = rl_metrics[1]
            
            diff = abs(rl_length - osm_length)
            results.append((model_file, diff, rl_length, osm_length))
            
            if verbose:
                print(f"  {model_file.name}: diferencia = {diff/1000.0:.3f} km")
            
            if diff < best_diff:
                best_diff = diff
                best_model = model_file
                
        except Exception as e:
            if verbose:
                print(f"[WARNING] error evaluando {model_file.name}: {e}")
            continue
    
    if best_model is None:
        raise RuntimeError("ningún modelo produjo un resultado válido")
    
    if verbose:
        print(f"\n[INFO] resultados de evaluación:")
        for model, diff, rl_len, osm_len in sorted(results, key=lambda x: x[1])[:5]:
            print(f"  {model.name}: {diff/1000.0:.3f} km (rl={rl_len/1000.0:.3f}, osm={osm_len/1000.0:.3f})")
    
    return str(best_model), best_diff


def main() -> None:
    args = parse_args()

    # Cargar grafo según el método proporcionado
    subgraph_path = None
    if args.subgraph:
        # Cargar subgrafo
        subgraph_path = Path(args.subgraph)
        if not subgraph_path.is_absolute():
            # Si es relativo, asumir que está en scripts/ o relativo al directorio actual
            if not subgraph_path.exists():
                # Intentar desde scripts/
                script_dir = Path(__file__).parent.parent.parent / "scripts"
                subgraph_path = script_dir / args.subgraph
        
        print(f"[INFO] Cargando subgrafo desde: {subgraph_path}")
        # Cargar el grafo original (sin relabel) para visualización
        from src.data.download_graph import load_graph_from_graphml
        G_osm = load_graph_from_graphml(str(subgraph_path))
        # Cargar también el grafo relabeled para el entorno
        graph_relabel, node_to_idx, idx_to_node = load_subgraph_from_file(str(subgraph_path))
    else:
        # Cargar desde localidad (comportamiento original)
        _, node_to_idx, idx_to_node, G_osm = get_graph_relabel(args.place, return_original=True)

    base_start_idx = args.start
    base_dest_idx = args.destination if args.destination not in (None, -1) else max(idx_to_node.keys())

    if base_start_idx not in idx_to_node:
        raise ValueError(f"Índice de inicio {base_start_idx} no pertenece al grafo")
    validate_indices(list(args.waypoints), idx_to_node, "Waypoints")
    if base_dest_idx not in idx_to_node:
        raise ValueError(f"Índice de destino {base_dest_idx} no pertenece al grafo")
    
    # verificar que los nodos osm existan en el grafo (útil para subgrafos)
    if args.verbose or args.subgraph:
        start_osm = idx_to_node.get(base_start_idx)
        dest_osm = idx_to_node.get(base_dest_idx)
        if start_osm and start_osm not in G_osm:
            print(f"[WARNING] nodo osm {start_osm} (índice {base_start_idx}) no encontrado en G_osm")
        if dest_osm and dest_osm not in G_osm:
            print(f"[WARNING] nodo osm {dest_osm} (índice {base_dest_idx}) no encontrado en G_osm")

    if args.compare:
        if not args.model_path and not args.model_dir and not args.find_best:
            raise ValueError("--compare requiere proporcionar --model-path, --model-dir o --find-best")
        
        # encontrar el mejor modelo si se solicita
        if args.find_best or args.model_dir:
            best_model_path, best_diff = find_best_model(
                model_dir=args.model_dir,
                model_path=args.model_path,
                subgraph_path=str(subgraph_path) if args.subgraph else None,
                place=args.place if not args.subgraph else None,
                start_idx=base_start_idx,
                destination_idx=base_dest_idx,
                waypoints=args.waypoints,
                idx_to_node=idx_to_node,
                G_osm=G_osm,
                max_steps=args.max_steps,
                deterministic=args.deterministic,
                verbose=args.verbose,
            )
            if args.verbose:
                print(f"\n[INFO] Mejor modelo encontrado: {best_model_path}")
                print(f"[INFO] Diferencia con OSMnx: {best_diff/1000.0:.3f} km")
            args.model_path = best_model_path

        # Preparar argumentos para run_episode según el método de carga
        episode_kwargs = {
            "model_path": args.model_path,
            "start": base_start_idx,
            "waypoints": args.waypoints,
            "destination": base_dest_idx,
            "max_steps": args.max_steps,
            "deterministic": args.deterministic,
            "verbose": args.verbose,
        }
        if args.subgraph:
            episode_kwargs["subgraph_path"] = str(subgraph_path)
        else:
            episode_kwargs["place"] = args.place
        
        rl_result = run_episode(**episode_kwargs)
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
        # Preparar argumentos para run_episode según el método de carga
        episode_kwargs = {
            "model_path": args.model_path,
            "start": base_start_idx,
            "waypoints": args.waypoints,
            "destination": base_dest_idx,
            "max_steps": args.max_steps,
            "deterministic": args.deterministic,
            "verbose": args.verbose,
        }
        if args.subgraph:
            episode_kwargs["subgraph_path"] = str(subgraph_path)
        else:
            episode_kwargs["place"] = args.place
        
        rl_result = run_episode(**episode_kwargs)
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
