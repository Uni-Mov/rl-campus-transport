"""Utilidad para ejecutar un episodio con un modelo PPO entrenado."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from stable_baselines3 import PPO

# Habilitar imports relativos cuando se ejecuta como script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.envs import create_masked_waypoint_env 
from src.data.download_graph import get_graph_relabel, load_subgraph_from_file  
from src.training.main import build_node_embeddings  
from src.utils.config_loader import load_config
import networkx as nx 


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generar un camino usando un modelo PPO entrenado")
    parser.add_argument("--place", type=str, default="Rio Cuarto, Cordoba, Argentina", help="Localidad a cargar")
    parser.add_argument("--model-path", type=str, default="ppo_waypoint_masked.zip", help="Ruta al modelo .zip")
    parser.add_argument("--start", type=int, default=0, help="Nodo inicial")
    parser.add_argument("--waypoints", type=int, nargs="*", default=[], help="Waypoints a visitar (orden libre)")
    parser.add_argument("--destination", type=int, default=-1, help="Nodo destino (por defecto ultimo nodo)")
    parser.add_argument("--max-steps", type=int, default=None, help="Pasos maximos del episodio")
    parser.add_argument("--deterministic", action="store_true", help="Usar politicas deterministicas")
    parser.add_argument("--verbose", action="store_true", help="Imprimir paso a paso")
    return parser.parse_args()


def run_episode(
    *,
    place: Optional[str] = None,
    subgraph_path: Optional[str] = None,
    graph: Optional[nx.MultiDiGraph] = None,
    node_to_idx: Optional[Dict] = None,
    idx_to_node: Optional[Dict] = None,
    model_path: str,
    start: int,
    waypoints: Optional[List[int]] = None,
    destination: Optional[int] = None,
    max_steps: Optional[int] = None,
    deterministic: bool = True,
    verbose: bool = False,
) -> Dict[str, object]:
    """Ejecuta un episodio y devuelve estadisticas y recorrido.
    
    Args:
        place: localidad para cargar el grafo (si no se proporciona graph o subgraph_path)
        subgraph_path: ruta a un archivo .graphml del subgrafo
        graph: grafo directamente (si ya está cargado)
        node_to_idx: mapeo de nodos a índices (requerido si se pasa graph)
        idx_to_node: mapeo de índices a nodos (requerido si se pasa graph)
        model_path: ruta al modelo PPO
        start: nodo inicial
        waypoints: waypoints a visitar
        destination: nodo destino
        max_steps: pasos máximos
        deterministic: usar política determinística
        verbose: mostrar logs
    """

    waypoints = list(waypoints or [])
    
    # Cargar grafo según el método proporcionado
    if graph is not None:
        if node_to_idx is None or idx_to_node is None:
            raise ValueError("node_to_idx e idx_to_node son requeridos cuando se proporciona graph")
    elif subgraph_path is not None:
        graph, node_to_idx, idx_to_node = load_subgraph_from_file(subgraph_path)
    elif place is not None:
        graph, node_to_idx, idx_to_node = get_graph_relabel(place)
    else:
        raise ValueError("Debe proporcionarse place, subgraph_path o graph")
    
    n_nodes = graph.number_of_nodes()

    destination = destination if destination is not None and destination >= 0 else (n_nodes - 1)

    if start not in graph.nodes:
        raise ValueError(f"Nodo inicial {start} no existe en el grafo")
    for wp in waypoints:
        if wp not in graph.nodes:
            raise ValueError(f"Waypoint {wp} no existe en el grafo")
    if destination not in graph.nodes:
        raise ValueError(f"Destino {destination} no existe en el grafo")

    max_steps = max_steps if max_steps is not None else int(max(1, n_nodes * 0.8))

    node_embeddings = build_node_embeddings(graph)

    CONFIG_PATH = Path(__file__).resolve().parents[1] / "envs" / "config" / "config.yaml"
    cfg = load_config(CONFIG_PATH)
    environment_cfg, rewards_cfg = cfg["environment"], cfg["rewards"]
    env = create_masked_waypoint_env(graph, waypoints, start, destination, environment_cfg, rewards_cfg)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontro el modelo en {model_path}")

    model = PPO.load(model_path, env=env)

    obs, info = env.reset()
    done = False
    truncated = False
    total_reward = 0.0
    steps = 0

    if verbose:
        print(f"Inicio: nodo {env.current_node}")
        print(f"Waypoints pendientes: {waypoints}")
        print(f"Destino: {destination}")
        print(f"Max steps: {max_steps}")
        print("---")

    while not (done or truncated):
        action, _ = model.predict(obs, deterministic=deterministic)
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        steps += 1

        if verbose:
            mask_applied = info.get("masking_applied", 0)
            print(
                f"Paso {steps:03d} -> nodo {env.current_node}, "
                f"reward={reward:.2f}, mask={mask_applied}, remaining={info.get('remaining_waypoints', [])}"
            )

        if steps >= max_steps * 2:
            truncated = True
            info["terminated_reason"] = "manual_limit"
            break

    path = info.get("path", [])

    return {
        "path": path,
        "done": done,
        "truncated": truncated,
        "steps": steps,
        "total_reward": total_reward,
        "info": info,
        "environment_cfg": environment_cfg,
        "rewards_cfg": rewards_cfg,
        "graph": graph,
        "node_to_idx": node_to_idx,
        "idx_to_node": idx_to_node,
    }


def main() -> None:
    args = parse_args()
    result = run_episode(
        place=args.place,
        model_path=args.model_path,
        start=args.start,
        waypoints=args.waypoints,
        destination=args.destination,
        max_steps=args.max_steps,
        deterministic=args.deterministic,
        verbose=args.verbose,
    )

    print("\nResultado")
    print("========")
    if result["done"]:
        print("Termino en destino")
    elif result["truncated"]:
        reason = result["info"].get("terminated_reason", "max_steps")
        print(f"Terminado por truncado ({reason})")
    else:
        print("Termino sin exito")

    print(f"Pasos: {result['steps']}")
    print(f"Recompensa acumulada: {result['total_reward']:.2f}")
    print(f"Camino: {result['path']}")


if __name__ == "__main__":
    main()
