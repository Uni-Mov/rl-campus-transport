import gymnasium as gym
import numpy as np
import pickle
import os
from collections import deque, defaultdict
from src.utils.distances import precalculate_distances
from .waypoint_navigation import WaypointNavigationEnv
from pathlib import Path


class ActionMaskingWrapper(gym.Wrapper):
    """
    Wrapper para aplicar action masking y detección de ciclos.

    - Filtra acciones inválidas y repetitivas
    - Penaliza bucles cortos o visitas excesivas
    - Puede truncar el episodio si detecta un ciclo grave
    """

    def __init__(self, env, debug: bool = False, distances: dict | None = None, distances_path: str | None = None):
        super().__init__(env)
        self.env = env
        self.debug = debug
        # ciclo / tracking
        self.recent_nodes = deque(maxlen=10)
        self.recent_nodes_set = set()
        self.visit_counter = defaultdict(int)
        # action masking
        self.action_mask = np.zeros(self.env.max_actions, dtype=bool)
        self._base_mask = np.ones(self.env.max_actions, dtype=bool)
        # short-path caching and precomputed distances
        self._sp_cache = {}
        self._sp_cache_max = 50000
        self._distances = None
        if distances is not None:
            self._distances = distances
        elif distances_path is not None and os.path.exists(distances_path):
            try:
                with open(distances_path, "rb") as fh:
                    self._distances = pickle.load(fh)
            except Exception:
                if self.debug:
                    print("Failed to load distances from", distances_path)
                self._distances = None

    def _neighbors(self):
        if hasattr(self.env, "_ordered_neighbors"):
            return self.env._ordered_neighbors(self.env.current_node)
        return list(self.env.graph.neighbors(self.env.current_node))

    def _update_action_mask_with_cycles(self):
        neighbors = self._neighbors()
        max_a = self.env.max_actions
        if len(neighbors) > max_a:
            neighbors = neighbors[:max_a]

        self.action_mask.fill(False)

        env_mask_fn = getattr(self.env, "_action_mask", None)
        if callable(env_mask_fn):
            self._base_mask = env_mask_fn().astype(bool)
        else:
            self._base_mask.fill(True)

        remaining_waypoints = list(getattr(self.env, "remaining_waypoints", []))
        destination = getattr(self.env, "destination", None)

        targets = remaining_waypoints[:] if remaining_waypoints else [destination] if destination is not None else []
        sp_fn = getattr(self.env, "_sp_length", None)

        # dist_cache: prev dist desde current_node a cada target
        dist_cache = {}
        if self._distances and targets:
            cur = self.env.current_node
            for target in targets:
                try:
                    dist_cache[target] = self._distances.get(cur, {}).get(target, np.inf)
                except Exception:
                    dist_cache[target] = np.inf
        elif sp_fn and targets:
            for target in targets:
                try:
                    key = (self.env.current_node, target)
                    if key in self._sp_cache:
                        dist_cache[target] = self._sp_cache[key]
                    else:
                        dist = sp_fn(self.env.current_node, target)
                        self._sp_cache[key] = dist
                        dist_cache[target] = dist
                except Exception:
                    dist_cache[target] = np.inf

            if len(self._sp_cache) > self._sp_cache_max:
                self._sp_cache.clear()

        recent_set = self.recent_nodes_set
        base_mask = self._base_mask
        any_valid = False

        for i, neighbor in enumerate(neighbors):
            if i >= max_a:
                break
            if not base_mask[i]:
                continue

            # si es waypoint o destino directo, siempre válido
            if neighbor in remaining_waypoints or (not remaining_waypoints and neighbor == destination):
                self.action_mask[i] = True
                any_valid = True
                continue

            closer = False
            # primero intentar usar distancias precomputadas
            if targets:
                for target in targets:
                    prev_dist = dist_cache.get(target, np.inf)
                    neighbor_dist = np.inf
                    if self._distances:
                        neighbor_dist = self._distances.get(neighbor, {}).get(target, np.inf)
                    elif sp_fn:
                        try:
                            key = (neighbor, target)
                            if key in self._sp_cache:
                                neighbor_dist = self._sp_cache[key]
                            else:
                                neighbor_dist = sp_fn(neighbor, target)
                                self._sp_cache[key] = neighbor_dist
                        except Exception:
                            neighbor_dist = np.inf
                    # requerir mejora ligera (evitar empates/oscillaciones): permitir hasta 0.5% peor
                    # usar 0.995 para preferir movimientos que reduzcan la distancia
                    try:
                        if np.isfinite(prev_dist) and np.isfinite(neighbor_dist):
                            if neighbor_dist <= prev_dist * 0.995:
                                closer = True
                        else:
                            # fallback: si no hay datos, permitir
                            closer = True
                    except Exception:
                        closer = True
                    if closer:
                        break
            if targets and not closer:
                continue

            # evitar loops cortos, pero no bloquear si es única opción
            if neighbor in recent_set or self.visit_counter.get(neighbor, 0) >= 3:
                continue

            self.action_mask[i] = True
            any_valid = True

        # si nada quedó habilitado, liberar al menos alguna acción
        if not any_valid:
            for i, neighbor in enumerate(neighbors):
                if i < len(base_mask) and base_mask[i]:
                    self.action_mask[i] = True
            # limpiar historial para permitir moverse
            self.recent_nodes.clear()

        # fallback final: asegurar al menos una acción válida
        if not np.any(self.action_mask) and neighbors:
            valid_idx = np.where(base_mask[:len(neighbors)])[0]
            if valid_idx.size > 0:
                self.action_mask[valid_idx[0]] = True

    def _get_valid_action_fallback(self):
        valid_actions = np.where(self.action_mask)[0]
        if len(valid_actions) == 0:
            return 0

        remaining_waypoints = getattr(self.env, "remaining_waypoints", [])
        destination = getattr(self.env, "destination", None)
        neighbors = self._neighbors()

        for idx in valid_actions:
            if idx < len(neighbors):
                neighbor = neighbors[idx]
                if neighbor in remaining_waypoints:
                    return int(idx)
        if not remaining_waypoints and destination is not None:
            for idx in valid_actions:
                if idx < len(neighbors) and neighbors[idx] == destination:
                    return int(idx)
        return int(np.random.choice(valid_actions))

    def _update_cycle_tracking(self):
        self.recent_nodes.append(self.env.current_node)
        self.visit_counter[self.env.current_node] += 1
        # mantener set para membership O(1)
        self.recent_nodes_set.add(self.env.current_node)
        # reconstruir set a partir del deque (deque es pequeño, coste bajo)
        self.recent_nodes_set = set(self.recent_nodes)

    def _calculate_cycle_penalty(self):
        # Devuelve el penalty "crudo" (un valor negativo) en unidades absolutas.
        visit_count = self.visit_counter[self.env.current_node]
        if visit_count > 3:
            base = getattr(self.env, "anti_loop_penalty", 20.0)
            raw = -float(base) * (visit_count - 3)
        else:
            raw = 0.0
        # limitar el raw penalty a un mínimo (consistente con comportamiento previo)
        if raw < -300.0:
            raw = -300.0
        return raw

    def _initialize_cycle_tracking(self):
        self.recent_nodes = deque([self.env.current_node], maxlen=10)
        self.recent_nodes_set = {self.env.current_node}
        self.visit_counter = defaultdict(int)
        self.visit_counter[self.env.current_node] = 1

    def step(self, action):
        self._update_action_mask_with_cycles()
        orig_action = int(action)
        if action >= self.env.max_actions or not self.action_mask[action]:
            action = self._get_valid_action_fallback()
        # soportar env.step que devuelva 4-tupla (gym) o 5-tupla (gymnasium)
        result = self.env.step(action)
        if len(result) == 4:
            obs, reward, done, info = result
            truncated = False
        else:
            obs, reward, done, truncated, info = result

        self._update_cycle_tracking()

        # Usar valor raw para que VC2Normalizer pueda aplicar su normalización adaptativa
        cycle_penalty = float(self._calculate_cycle_penalty())
        try:
            reward = float(reward) + cycle_penalty
        except Exception:
            # si reward no es un escalar simple, intentar convertir
            try:
                reward = float(np.asarray(reward).item()) + cycle_penalty
            except Exception:
                # fallback: dejar reward sin cambiar si no convertible
                pass

        # truncar si el raw penalty excede el umbral severo (comportamiento previo)
        if raw_cycle_penalty <= -300.0:
            truncated = True
            info = dict(info or {})
            info["terminated_reason"] = "loop_detected"

        info = dict(info or {})
        info["action_mask"] = self.action_mask.copy()
        info["masking_applied"] = int(action != orig_action)
        info["original_action"] = orig_action
        info["chosen_action"] = int(action)
        info["valid_actions"] = np.where(self.action_mask)[0].tolist()

        # devolver en la misma forma que recibió del env interno
        if len(result) == 4 and truncated is False:
            return obs, reward, done, info
        return obs, reward, done, truncated, info

    def reset(self, **kwargs):
        # aceptar env.reset() -> obs  o env.reset() -> (obs, info)
        res = self.env.reset(**kwargs)
        if isinstance(res, tuple) and len(res) == 2:
            obs, info = res
        else:
            obs = res
            info = {}
        self._initialize_cycle_tracking()
        self._update_action_mask_with_cycles()
        return obs, info

    @property
    def current_node(self):
        return self.env.current_node

def create_masked_waypoint_env(
    graph,
    waypoints,
    start_node,
    destination,
    env_cfg: dict | None = None,
    rew_cfg: dict | None = None,
    debug: bool = False,
    distances: dict | None = None,
    distances_path: str | None = None,
):
    """
    Crea un entorno WaypointNavigationEnv usando configuración YAML.
    """
    if isinstance(waypoints, int):
        waypoints = [waypoints]
        
    env = WaypointNavigationEnv(
        graph=graph,
        start_node=start_node,
        waypoints=waypoints,
        destination=destination,
        env_cfg=env_cfg or {},
        rew_cfg=rew_cfg or {},
    )
    
    # Si no se pasaron distancias explícitamente, intentar obtenerlas del grafo
    if distances is None and hasattr(graph, "graph"):
        graph_distances = graph.graph.get("distances")
        if graph_distances is not None:
            distances = graph_distances
    
    # si no se pasó distances_path, intentar autodescubrir en ia_ml/src/data
    if distances_path is None:
        data_dir = (Path(__file__).parent.parent / "data").resolve()
        try:
            if data_dir.exists():
                candidates = list(data_dir.glob("*_distances.pkl"))
                if candidates:
                    chosen = None
                    # intentar emparejar por nombre del grafo si está disponible
                    graph_name = None
                    try:
                        graph_name = getattr(graph, "name", None)
                    except Exception:
                        graph_name = None
                    if not graph_name and hasattr(graph, "graph"):
                        try:
                            graph_name = graph.graph.get("name")
                        except Exception:
                            graph_name = None

                    if graph_name:
                        for c in candidates:
                            if graph_name in c.stem:
                                chosen = c
                                break
                    if chosen is None and len(candidates) == 1:
                        chosen = candidates[0]
                    if chosen is not None:
                        distances_path = str(chosen)
        except Exception:
            # no crítico, continuamos sin precomputed distances
            distances_path = distances_path

    # Si no se encontró distances_path ni se pasaron distancias, intentar precalcular y cachear
    if distances is None and distances_path is None:
        try:
            # intentar obtener un nombre identificador para el grafo
            graph_name = None
            try:
                graph_name = getattr(graph, "name", None)
            except Exception:
                graph_name = None
            if not graph_name and hasattr(graph, "graph"):
                try:
                    graph_name = graph.graph.get("name")
                except Exception:
                    graph_name = None

            fname = (graph_name or "graph") + "_distances.pkl"
            chosen_path = (Path(__file__).parent.parent / "data" / fname).resolve()
            # si no existe, precalcular (esto puede tardar para grafos grandes)
            if not chosen_path.exists():
                # precalculate_distances espera un NetworkX graph
                print(f"[distances] No distance cache found; precalculating and saving to {chosen_path} (this may take time)...")
                # ensure data dir exists
                chosen_path.parent.mkdir(parents=True, exist_ok=True)
                shortest_paths = precalculate_distances(graph, cache_path=str(chosen_path))
                distances = shortest_paths
                distances_path = str(chosen_path)
            else:
                # cargar cache existente
                try:
                    with open(str(chosen_path), "rb") as fh:
                        distances = pickle.load(fh)
                        distances_path = str(chosen_path)
                except Exception:
                    # si falla la carga, intentar recalcular
                    print("[distances] Failed to load existing distances cache; recalculating...")
                    shortest_paths = precalculate_distances(graph, cache_path=str(chosen_path))
                    distances = shortest_paths
                    distances_path = str(chosen_path)
        except Exception as e:
            if getattr(globals().get("__builtins__", {}), "print", None):
                print(f"[distances] Precompute attempt failed: {e}")
            distances = distances

    return ActionMaskingWrapper(env, debug=debug, distances=distances, distances_path=distances_path)
