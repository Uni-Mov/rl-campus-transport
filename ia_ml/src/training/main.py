"""Entrenamiento de WaypointNavigationEnv con action masking activo."""

from __future__ import annotations

import os
from typing import Dict, Any, Tuple
from pathlib import Path
import networkx as nx
import numpy as np
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
from stable_baselines3.common.monitor import Monitor
from src.envs import create_masked_waypoint_env 
from src.data.download_graph import (
    get_graph_relabel,
    load_graph_from_graphml,
    relabel_nodes_to_indices,
    load_distances_if_present,
)
from src.utils.config_loader import load_config
from src.utils.embeddings import build_node_embeddings 


def make_env(graph, start_node, waypoints, destination, environment_cfg: Dict, rewards_cfg: Dict):
    return create_masked_waypoint_env(graph, waypoints, start_node, destination, environment_cfg, rewards_cfg)


def get_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "envs" / "config" / "config.yaml"


def load_configs() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    cfg = load_config(get_config_path())
    environment_cfg = cfg.get("environment", {})
    rewards_cfg = cfg.get("rewards", {})
    ppo_cfg = cfg.get("ppo", {})
    eval_cfg = cfg.get("evaluation", {})
    return cfg, environment_cfg, rewards_cfg, ppo_cfg, eval_cfg


def get_float(d: Dict[str, Any], key: str, default: float) -> float:
    val = d.get(key, default)
    try:
        return float(val)
    except (TypeError, ValueError):
        return float(default)


def get_int(d: Dict[str, Any], key: str, default: int) -> int:
    val = d.get(key, default)
    try:
        return int(val)
    except (TypeError, ValueError):
        return int(default)


def get_bool(d: Dict[str, Any], key: str, default: bool) -> bool:
    val = d.get(key, default)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "y", "t"}
    return bool(default)


def resolve_device(ppo_cfg: Dict[str, Any]) -> str:
    requested = str(ppo_cfg.get("device", "auto")).lower()
    if requested == "cpu":
        return "cpu"
    if requested == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_graph_from_cfg(cfg: Dict[str, Any]) -> nx.MultiDiGraph:
    graph_cfg: Dict[str, Any] = cfg.get("graph", {})
    source = str(graph_cfg.get("source", "place")).lower()
    if source == "file":
        path = graph_cfg.get("path") or ""
        if not path:
            raise ValueError("Config 'graph.path' requerido cuando source == 'file'")
        print(f"Cargando grafo desde archivo: {path}")
        G_osm = load_graph_from_graphml(path)
        distances_path = graph_cfg.get("distances_path") or ""
        if distances_path:
            distances = load_distances_if_present(distances_path)
            if distances is not None:
                G_osm.graph["distances"] = distances
        G_relabeled, _, _ = relabel_nodes_to_indices(G_osm)
        return G_relabeled
    place = graph_cfg.get("place") or "Río Cuarto, Cordoba, Argentina"
    print(f"Preparando grafo para: {place}")
    G_relabeled, _, _ = get_graph_relabel(place)
    return G_relabeled


def build_navigation_params(graph: nx.MultiDiGraph) -> Tuple[int, int, list[int], int]:
    n_nodes = graph.number_of_nodes()
    print(f"Grafo obtenido con {n_nodes} nodos")
    waypoints = [20, 35, int(n_nodes * 0.3), int(n_nodes * 0.7)]
    destination = n_nodes - 1
    start_node = 0
    max_steps = int(n_nodes * 0.8)
    return start_node, destination, waypoints, max_steps


def build_policy_kwargs(ppo_cfg: Dict[str, Any]) -> Dict[str, Any]:
    net_arch = ppo_cfg.get("net_arch", [256, 128, 64])
    return dict(net_arch=list(net_arch)) if net_arch is not None else {}


def build_model(env, ppo_cfg: Dict[str, Any], policy_kwargs: Dict[str, Any], device: str, tensorboard_log: str | None = None) -> PPO:
    policy = ppo_cfg.get("policy", "MlpPolicy")
    return PPO(
        policy,
        env,
        learning_rate=get_float(ppo_cfg, "learning_rate", 3e-4),
        n_steps=get_int(ppo_cfg, "n_steps", 1024),
        batch_size=get_int(ppo_cfg, "batch_size", 256),
        gamma=get_float(ppo_cfg, "gamma", 0.99),
        clip_range=get_float(ppo_cfg, "clip_range", 0.2),
        ent_coef=get_float(ppo_cfg, "ent_coef", 0.01),
        vf_coef=get_float(ppo_cfg, "vf_coef", 0.5),
        policy_kwargs=policy_kwargs,
        verbose=get_int(ppo_cfg, "verbose", 1),
        device=device,
        tensorboard_log=tensorboard_log,
    )


def build_callbacks(eval_env, eval_cfg: Dict[str, Any]) -> EvalCallback:
    early_cfg = eval_cfg.get("early_stop", {})
    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=get_int(early_cfg, "max_no_improvement_evals", 8),
        min_evals=get_int(early_cfg, "min_evals", 3),
        verbose=get_int(early_cfg, "verbose", 1),
    )
    return EvalCallback(
        eval_env,
        best_model_save_path=eval_cfg.get("best_model_save_path", "./logs/best_model_masked/"),
        log_path=eval_cfg.get("log_path", "./logs/results_masked/"),
        eval_freq=get_int(eval_cfg, "eval_freq", 5000),
        n_eval_episodes=get_int(eval_cfg, "n_eval_episodes", 5),
        deterministic=get_bool(eval_cfg, "deterministic", True),
        callback_after_eval=stop_callback,
        verbose=get_int(eval_cfg, "verbose", 1),
    )


def demo_episode(env, model: PPO, waypoints: list[int], destination: int, max_steps: int) -> None:
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
            print(f" paso {step + 1}: nodo {env.current_node}, reward={reward:.2f}, mask={mask_applied}")
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


def main() -> None:
    # cargar configuraciones
    cfg, environment_cfg, rewards_cfg, ppo_cfg, eval_cfg = load_configs()

    # cargar grafo y parámetros de navegación
    graph = load_graph_from_cfg(cfg)
    start_node, destination, waypoints, max_steps = build_navigation_params(graph)

    # configurar directorios de logs
    train_log_dir = eval_cfg.get("train_log_dir", "./logs/training/")
    eval_log_dir = eval_cfg.get("log_path", "./logs/results_masked/")
    tensorboard_log = ppo_cfg.get("tensorboard_log") or eval_cfg.get("tensorboard_log", "./logs/tensorboard/")
    
    # crear directorios si no existen
    os.makedirs(train_log_dir, exist_ok=True)
    os.makedirs(eval_log_dir, exist_ok=True)
    if tensorboard_log:
        os.makedirs(tensorboard_log, exist_ok=True)

    # construir entornos 
    base_env = make_env(graph, start_node, waypoints, destination, environment_cfg, rewards_cfg)
    base_eval_env = make_env(graph, start_node, waypoints, destination, environment_cfg, rewards_cfg)
    
    # envolver entornos con Monitor para registrar recompensas
    env = Monitor(base_env, train_log_dir)
    eval_env = Monitor(base_eval_env, eval_log_dir)

    # modelo
    device = resolve_device(ppo_cfg)
    print(f"Usando dispositivo: {device}")
    if tensorboard_log:
        print(f"TensorBoard logs: {tensorboard_log}")
        print("  Para ver las métricas: tensorboard --logdir " + tensorboard_log)
    policy_kwargs = build_policy_kwargs(ppo_cfg)
    model = build_model(env, ppo_cfg, policy_kwargs, device, tensorboard_log=tensorboard_log)

    # entrenamiento
    total_timesteps = get_int(ppo_cfg, "total_timesteps", 250_000)
    # callbacks
    eval_callback = build_callbacks(eval_env, eval_cfg)
    model.learn(total_timesteps=total_timesteps, callback=eval_callback, progress_bar=True)
    model.save("ppo_waypoint_masked")

    # demo breve
    demo_episode(env, model, waypoints, destination, max_steps)


if __name__ == "__main__":
    main()
