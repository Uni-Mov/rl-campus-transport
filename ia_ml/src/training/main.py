"""Entrenamiento de WaypointNavigationEnv con action masking activo."""

from __future__ import annotations

import os
from typing import Dict, Any, Tuple
from pathlib import Path
import networkx as nx
import numpy as np
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    EvalCallback, 
    StopTrainingOnNoModelImprovement, 
    BaseCallback,
    CallbackList
)
from stable_baselines3.common.monitor import Monitor
from src.envs import create_masked_waypoint_env 
from src.envs.reward_normalizer import VC2Normalizer
from src.data.download_graph import (
    get_graph_relabel,
    load_graph_from_graphml,
    relabel_nodes_to_indices,
    load_distances_if_present,
)
from src.utils.config_loader import load_config
from src.utils.embeddings import build_node_embeddings 


def make_env(graph, start_node, waypoints, destination, environment_cfg: Dict, rewards_cfg: Dict):
    base = create_masked_waypoint_env(graph, waypoints, start_node, destination, environment_cfg, rewards_cfg)
    gamma = get_float(rewards_cfg, "norm_gamma", 0.99)
    clip = get_float(rewards_cfg, "norm_clip", 10.0)
    scale = get_float(rewards_cfg, "norm_scale", 1.0)
    return VC2Normalizer(base, gamma=gamma, clip_range=clip, scale=scale)


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
        G_relabeled, node_to_idx, idx_to_node = relabel_nodes_to_indices(G_osm)
        
        # Convertir distancias de IDs originales a índices relabeled
        if "distances" in G_osm.graph:
            converted = {}
            for orig_u, dist_dict in G_osm.graph["distances"].items():
                u_idx = node_to_idx.get(orig_u)
                if u_idx is None:
                    continue
                converted[u_idx] = {}
                for orig_v, d in dist_dict.items():
                    v_idx = node_to_idx.get(orig_v)
                    if v_idx is None:
                        continue
                    converted[u_idx][v_idx] = float(d)
            G_relabeled.graph["distances"] = converted
        
        return G_relabeled
    place = graph_cfg.get("place") or "Río Cuarto, Cordoba, Argentina"
    print(f"Preparando grafo para: {place}")
    G_relabeled, _, _ = get_graph_relabel(place)
    return G_relabeled


def build_navigation_params(graph: nx.MultiDiGraph) -> Tuple[int, int, list[int], int]:
    n_nodes = graph.number_of_nodes()
    print(f"Grafo obtenido con {n_nodes} nodos")
    
    # Waypoints escalados según tamaño del grafo
    if n_nodes < 100:
        waypoints = [20, 35, int(n_nodes * 0.3), int(n_nodes * 0.7)]
    elif n_nodes < 1000:
        waypoints = [int(n_nodes * 0.1), int(n_nodes * 0.3), int(n_nodes * 0.6), int(n_nodes * 0.8)]
    else:
        # Para grafos muy grandes, usar menos waypoints pero más estratégicos
        waypoints = [int(n_nodes * 0.2), int(n_nodes * 0.5), int(n_nodes * 0.8)]
    
    destination = n_nodes - 1
    start_node = 0
    
    # max_steps escalado logarítmicamente para grafos grandes
    base_steps = min(int(n_nodes * 0.5), 1000)  # limitar para eficiencia
    max_steps = base_steps
    
    print(f"Waypoints: {waypoints}")
    print(f"Max steps: {max_steps}")
    
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
        n_steps=get_int(ppo_cfg, "n_steps", 2048),
        batch_size=get_int(ppo_cfg, "batch_size", 512),
        n_epochs=get_int(ppo_cfg, "n_epochs", 10),
        gamma=get_float(ppo_cfg, "gamma", 0.99),
        clip_range=get_float(ppo_cfg, "clip_range", 0.2),
        ent_coef=get_float(ppo_cfg, "ent_coef", 0.01),
        vf_coef=get_float(ppo_cfg, "vf_coef", 0.5),
        max_grad_norm=get_float(ppo_cfg, "max_grad_norm", 0.5),
        policy_kwargs=policy_kwargs,
        verbose=get_int(ppo_cfg, "verbose", 1),
        device=device,
        tensorboard_log=tensorboard_log,
    )


class DebugCallback(BaseCallback):
    """
    Callback para mostrar información de debug cada 1000 pasos:
    - Path recorrido
    - Waypoints que faltan
    - Si pasó por el destino final
    """
    def __init__(self, verbose: int = 0, debug_freq: int = 1000):
        super().__init__(verbose)
        self.debug_freq = debug_freq
        self.last_episode_path = None
        self.last_episode_remaining_waypoints = None
        self.last_episode_destination_reached = False
        self.last_episode_current_node = None
        self.last_episode_terminated_reason = None
        self.last_episode_info = None
        self.episode_count = 0
        self.last_debug_step = 0
    
    def _on_step(self) -> bool:
        # Acceder a información del paso actual
        infos = self.locals.get("infos", [])
        dones = self.locals.get("dones", [])
        
        # Verificar si el episodio terminó (en cualquier vectorizado)
        for i, (done, info) in enumerate(zip(dones, infos)):
            if done or info.get("TimeLimit.truncated", False):
                # Guardar información del episodio que terminó
                self.last_episode_path = info.get("path", [])
                self.last_episode_remaining_waypoints = info.get("remaining_waypoints", [])
                self.last_episode_destination_reached = info.get("terminated_reason") == "destination_reached"
                self.last_episode_current_node = info.get("current_node", None)
                self.last_episode_terminated_reason = info.get("terminated_reason", None)
                self.last_episode_info = info.copy()  # Guardar info completo para debug
                self.episode_count += 1
        
        # Mostrar debug cada debug_freq pasos
        if self.num_timesteps - self.last_debug_step >= self.debug_freq:
            self.last_debug_step = self.num_timesteps
            
            # Si tenemos información del último episodio, mostrarla
            if self.last_episode_path is not None:
                print("\n" + "=" * 80)
                print(f"[DEBUG] Paso {self.num_timesteps} | Episodio #{self.episode_count}")
                print("=" * 80)
                
                # Mostrar path (truncar si es muy largo)
                path_str = str(self.last_episode_path)
                if len(path_str) > 150:
                    path_str = path_str[:150] + "..."
                print(f"Path recorrido: {path_str}")
                print(f"Longitud del path: {len(self.last_episode_path)} nodos")
                
                # Mostrar waypoints restantes
                if self.last_episode_remaining_waypoints:
                    print(f"Waypoints pendientes: {self.last_episode_remaining_waypoints}")
                else:
                    print("Waypoints pendientes: [] (todos completados)")
                
                # Mostrar si llegó al destino
                if self.last_episode_destination_reached:
                    print("destino final: ALCANZADO")
                else:
                    print("destino final: NO alcanzado")
                
                # Mostrar razón de terminación
                if self.last_episode_terminated_reason:
                    reason_display = {
                        "destination_reached": "llegó al destino",
                        "max_steps": "máximo de pasos alcanzado",
                        "max_wait_steps": "máximo de pasos de espera",
                        "dead_end": "callejón sin salida",
                        "loop_detected": "bucle detectado",
                        "time_limit": "límite de tiempo",
                    }.get(self.last_episode_terminated_reason, f"ℹ {self.last_episode_terminated_reason}")
                    print(f"razón de terminación: {reason_display}")
                else:
                    print("razón de terminación: No especificada")
                
                # Mostrar nodo final
                if self.last_episode_path:
                    print(f"Nodo final: {self.last_episode_path[-1]}")
                elif self.last_episode_current_node is not None:
                    print(f"nodo actual: {self.last_episode_current_node}")
                
                print("=" * 80 + "\n")
            else:
                # Si no hay información aún, mostrar mensaje
                print(f"\n[DEBUG] Paso {self.num_timesteps} - Esperando información del primer episodio...\n")
        
        return True


class PushValueStatsCallback(BaseCallback):
    """Callback que empuja las predicciones del crítico (values) al normalizador VC2.

    Debe inicializarse con la instancia del normalizador que envuelve el env base
    (es decir, la que devuelve `make_env`). En `on_rollout_end` accede al
    `rollout_buffer` del modelo y extrae los `values` para actualizar
    `rms_value` vía `push_value_batch`.
    """
    def __init__(self, normalizer, verbose: int = 0):
        super().__init__(verbose)
        self.normalizer = normalizer

    def _on_step(self) -> bool:
        """Método obligatorio de BaseCallback. Retorna True para continuar entrenamiento."""
        return True

    def _on_rollout_end(self) -> None:
        # SB3 almacena los valores predichos en rollout_buffer.values (torch tensor)
        try:
            buf = getattr(self.model, "rollout_buffer", None)
            if buf is None:
                return
            values = None
            # rollout_buffer may store 'values' or 'values_preds'
            if hasattr(buf, "values"):
                # Torch tensor
                values = buf.values
            elif hasattr(buf, "value_preds"):
                values = buf.value_preds
            if values is None:
                return
            # convert to numpy and push
            vals_np = values.cpu().numpy().ravel()
            self.normalizer.push_value_batch(vals_np)
        except Exception as e:
            if self.verbose:
                print(f"PushValueStatsCallback error: {e}")


def build_callbacks(eval_env, eval_cfg: Dict[str, Any], debug_freq: int = 1000) -> Tuple[EvalCallback, DebugCallback]:
    early_cfg = eval_cfg.get("early_stop", {})
    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=get_int(early_cfg, "max_no_improvement_evals", 8),
        min_evals=get_int(early_cfg, "min_evals", 3),
        verbose=get_int(early_cfg, "verbose", 1),
    )
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=eval_cfg.get("best_model_save_path", "./logs/best_model_masked/"),
        log_path=eval_cfg.get("log_path", "./logs/results_masked/"),
        eval_freq=get_int(eval_cfg, "eval_freq", 5000),
        n_eval_episodes=get_int(eval_cfg, "n_eval_episodes", 5),
        deterministic=get_bool(eval_cfg, "deterministic", True),
        callback_after_eval=stop_callback,
        verbose=get_int(eval_cfg, "verbose", 1),
    )
    debug_callback = DebugCallback(verbose=1, debug_freq=debug_freq)
    return eval_callback, debug_callback

def unwrap_env(env):
    """Devuelve el env interno más profundo (desempaqueta wrappers tipo Monitor, RewardNormalizer, etc.)."""
    e = env
    # algunos wrappers usan `.env`, otros `.unwrapped` — priorizamos `.env`
    while True:
        if hasattr(e, "env"):
            e = getattr(e, "env")
            continue
        if hasattr(e, "unwrapped") and e is not getattr(e, "unwrapped"):
            try:
                e = getattr(e, "unwrapped")
                continue
            except Exception:
                pass
        break
    return e

def demo_episode(env, model: PPO, waypoints: list[int], destination: int, max_steps: int) -> None:
    obs, info = env.reset()
    done = False
    truncated = False
    total_reward = 0.0

    inner = unwrap_env(env)
    # usar el env desempaquetado para acceder a atributos como current_node
    start_node = getattr(inner, "current_node", None)
    print(f"Inicio: nodo {start_node}")
    print(f"Objetivo: {waypoints} -> {destination}")
    print(f"Max steps: {max_steps}\n")

    for step in range(max_steps * 2):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        if step < 15 or done or truncated:
            mask_applied = info.get("masking_applied", 0)
            current_node = getattr(inner, "current_node", None)
            print(f" paso {step + 1}: nodo {current_node}, reward={reward:.2f}, mask={mask_applied}")
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
    eval_callback, debug_callback = build_callbacks(eval_env, eval_cfg, debug_freq=1000)
    # PushValueStatsCallback needs the original normalizer instance (base_env)
    push_value_callback = PushValueStatsCallback(normalizer=base_env, verbose=0)
    callback_list = CallbackList([eval_callback, debug_callback, push_value_callback])
    model.learn(total_timesteps=total_timesteps, callback=callback_list, progress_bar=True)
    model.save("ppo_waypoint_masked")

    # demo breve
    demo_episode(env, model, waypoints, destination, max_steps)


if __name__ == "__main__":
    main()
