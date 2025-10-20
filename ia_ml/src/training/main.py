"""Entrenamiento de WaypointNavigationEnv con action masking activo."""

from __future__ import annotations

import os
from typing import Dict
from pathlib import Path
import networkx as nx
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
from src.envs import create_masked_waypoint_env 
from src.data.download_graph import get_graph_relabel 
from src.utils.config_loader import load_config


def make_env(graph, start_node, waypoints, destination, environment_cfg: Dict, rewards_cfg: Dict):
    return create_masked_waypoint_env(graph, start_node, waypoints, destination, environment_cfg, rewards_cfg)


def main() -> None:
    # configuracion general
    CONFIG_PATH = Path(__file__).resolve().parents[1] / "envs" / "config" / "config.yaml"
    cfg = load_config(CONFIG_PATH)
    environment_cfg, rewards_cfg = cfg["environment"], cfg["rewards"]
    locality = "Guatimozin, Cordoba, Argentina"
    print(f"Preparando grafo para: {locality}")
    graph, _ , _  = get_graph_relabel(locality)

    n_nodes = graph.number_of_nodes()
    print(f"Grafo obtenido con {n_nodes} nodos")

    # configuración básica de navegación
    waypoints = [20, 35, int(n_nodes * 0.3), int(n_nodes * 0.7)]
    destination = n_nodes - 1
    start_node = 0

    max_steps = int(n_nodes * 0.8)

    env = make_env(graph, start_node, waypoints, destination, environment_cfg, rewards_cfg)

    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=256,
        gamma=0.99,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        policy_kwargs=dict(net_arch=[256, 128, 64]),
        verbose=1,
    )

    eval_env = make_env(graph, start_node, waypoints, destination, environment_cfg, rewards_cfg)

    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=8,
        min_evals=3,
        verbose=1,
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./logs/best_model_masked/",
        log_path="./logs/results_masked/",
        eval_freq=5_000,
        n_eval_episodes=5,
        deterministic=True,
        callback_after_eval=stop_callback,
        verbose=1,
    )

    total_timesteps = 250_000
    model.learn(total_timesteps=total_timesteps, callback=eval_callback, progress_bar=True)
    model.save("ppo_waypoint_masked")

    obs, info = env.reset()
    done = False
    truncated = False
    total_reward = 0.0

    print(f"Inicio: nodo {env.current_node}")
    print(f"Objetivo: {waypoints} -> {destination}")
    print(f"Max steps: {max_steps}\n")

    for step in range(max_steps * 2):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward

        if step < 15 or done or truncated:
            mask_applied = info.get("masking_applied", 0)
            print(
                f" paso {step + 1}: nodo {env.current_node}, "
                f"reward={reward:.2f}, mask={mask_applied}"
            )

        if done or truncated:
            break

    path = info.get("path", [])

    print("\n" + "=" * 60)
    if done:
        print(f"Éxito en {len(path)} pasos")
    elif truncated:
        print(f"Truncado después de {len(path)} pasos")
    else:
        print("Fallo")

    print(f"Recompensa acumulada: {total_reward:.0f}")
    print(f"Camino: {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
