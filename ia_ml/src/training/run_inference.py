"""Utilidad para ejecutar un episodio con un modelo PPO entrenado."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional

import numpy as np
from stable_baselines3 import PPO

# Habilitar imports relativos cuando se ejecuta como script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.envs import create_masked_waypoint_env  # noqa: E402
from src.data.download_graph import get_graph_relabel  # noqa: E402
from src.training.main import build_node_embeddings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generar un camino usando un modelo PPO entrenado")
    parser.add_argument("--place", type=str, default="Guatimozin, Cordoba, Argentina", help="Localidad a cargar")
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
    place: str,
    model_path: str,
    start: int,
    waypoints: Optional[List[int]] = None,
    destination: Optional[int] = None,
    max_steps: Optional[int] = None,
    deterministic: bool = True,
    verbose: bool = False,
) -> Dict[str, object]:
    """Ejecuta un episodio y devuelve estadisticas y recorrido."""

    waypoints = list(waypoints or [])
    graph, node_to_idx, idx_to_node = get_graph_relabel(place)
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

    env_kwargs = dict(
        node_embeddings=node_embeddings,
        start_node=start,
        max_steps=max_steps,
        weight_name="travel_time",
        anti_loop_penalty=20.0,
        move_cost_coef=0.01,
        progress_coef=5.0,
        waypoint_bonus=50.0,
        destination_bonus=200.0,
        no_progress_penalty=2.0,
        max_wait_steps=None,
    )

    env = create_masked_waypoint_env(graph, waypoints, destination, **env_kwargs)

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
        "env_kwargs": env_kwargs,
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
