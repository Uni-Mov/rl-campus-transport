import gymnasium as gym
import numpy as np
from collections import deque, defaultdict
from .waypoint_navigation import WaypointNavigationEnv


class ActionMaskingWrapper(gym.Wrapper):
    """
    Wrapper para aplicar action masking y detección de ciclos.

    - Filtra acciones inválidas y repetitivas
    - Penaliza bucles cortos o visitas excesivas
    - Puede truncar el episodio si detecta un ciclo grave
    """

    def __init__(self, env, debug: bool = False):
        super().__init__(env)
        self.env = env
        self.debug = debug
        self.recent_nodes = deque(maxlen=10)
        self.visit_counter = defaultdict(int)
        self.action_mask = np.zeros(self.env.max_actions, dtype=bool)
        self._base_mask = np.ones(self.env.max_actions, dtype=bool)

    def _neighbors(self):
        if hasattr(self.env, "_ordered_neighbors"):
            return self.env._ordered_neighbors(self.env.current_node)
        return list(self.env.graph.neighbors(self.env.current_node))

    def _update_action_mask_with_cycles(self):
        neighbors = self._neighbors()
        self.action_mask.fill(False)

        env_mask_fn = getattr(self.env, "_action_mask", None)
        if callable(env_mask_fn):
            self._base_mask = env_mask_fn().astype(bool)
        else:
            self._base_mask.fill(True)

        remaining_waypoints = list(getattr(self.env, "remaining_waypoints", []))
        destination = getattr(self.env, "destination", None)

        targets = remaining_waypoints[:] if remaining_waypoints else [destination] if destination is not None else []
        dist_cache = {}
        if hasattr(self.env, "_sp_length") and targets:
            for target in targets:
                try:
                    dist_cache[target] = self.env._sp_length(self.env.current_node, target)
                except Exception:
                    dist_cache[target] = np.inf

        for i, neighbor in enumerate(neighbors):
            if i >= self.env.max_actions:
                break
            if not self._base_mask[i]:
                continue

            if neighbor in remaining_waypoints or (not remaining_waypoints and neighbor == destination):
                self.action_mask[i] = True
                continue

            closer = False
            # el wrapper calcula si moverse a un vecino deja al 
            # agente más cerca del objetivo que quedarse donde está.
            if targets and hasattr(self.env, "_sp_length"):
                for target in targets:
                    prev_dist = dist_cache.get(target, np.inf)
                    try:
                        neighbor_dist = self.env._sp_length(neighbor, target)
                    except Exception:
                        neighbor_dist = np.inf
                    if neighbor_dist < prev_dist:
                        closer = True
                        break
            if targets and not closer:
                continue

            if neighbor in self.recent_nodes:
                continue
            if self.visit_counter.get(neighbor, 0) >= 3:
                continue

            self.action_mask[i] = True

        if not np.any(self.action_mask) and neighbors:
            valid_idx = np.where(self._base_mask[:len(neighbors)])[0]
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

    def _calculate_cycle_penalty(self):
        cycle_penalty = 0
         # ida y vuelta
        if len(self.recent_nodes) >= 2:
            if self.recent_nodes[-1] == self.recent_nodes[-2]:
                cycle_penalty = -100  # volver directamente atrás
                
        if len(self.recent_nodes) >= 5:
            recent = list(self.recent_nodes)[-5:]
            if len(set(recent)) < 3:
                cycle_penalty = -300

        if len(self.recent_nodes) == 10:
            recent = list(self.recent_nodes)[-5:]
            previous = list(self.recent_nodes)[-10:-5]
            if recent == previous:
                cycle_penalty = max(cycle_penalty, -100)

        visit_count = self.visit_counter[self.env.current_node]
        if visit_count > 2:
            cycle_penalty = max(cycle_penalty, -50 * (visit_count - 2))

        return cycle_penalty

    def _initialize_cycle_tracking(self):
        self.recent_nodes = deque([self.env.current_node], maxlen=10)
        self.visit_counter = defaultdict(int)
        self.visit_counter[self.env.current_node] = 1

    def step(self, action):
        self._update_action_mask_with_cycles()
        orig_action = int(action)
        if action >= self.env.max_actions or not self.action_mask[action]:
            action = self._get_valid_action_fallback()

        obs, reward, done, truncated, info = self.env.step(action)
        self._update_cycle_tracking()

        cycle_penalty = self._calculate_cycle_penalty()
        reward += cycle_penalty

        if cycle_penalty <= -300:
            truncated = True
            info["terminated_reason"] = "loop_detected"

        info = dict(info or {})
        info["action_mask"] = self.action_mask.copy()
        info["masking_applied"] = int(action != orig_action)
        info["original_action"] = orig_action
        info["chosen_action"] = int(action)
        info["valid_actions"] = np.where(self.action_mask)[0].tolist()

        return obs, reward, done, truncated, info

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
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
    return ActionMaskingWrapper(env, debug=debug)
