import gymnasium as gym
import numpy as np
from collections import deque, defaultdict
from .waypoint_navigation import WaypointNavigationEnv


class ActionMaskingWrapper(gym.Wrapper):
    """wrapper para action masking y detección de ciclos"""

    def __init__(
        self,
        env,
        debug: bool = False,
        distances: dict | None = None,
        distances_path: str | None = None,
        action_masking_cfg: dict | None = None,
    ):
        super().__init__(env)
        self.env = env
        self.debug = debug

        self.recent_nodes = deque(maxlen=10)
        self.recent_nodes_set = set()
        self.visit_counter = defaultdict(int)

        self.action_mask = np.zeros(self.env.max_actions, dtype=bool)
        self._distances = distances

        self._sp_cache = {}
        self._sp_cache_max = 20000

    def _neighbors(self):
        return list(self.env.graph.neighbors(self.env.current_node))

    def _update_action_mask_with_cycles(self):
        # aplicar masking de acciones y evitar ciclos
        neighbors = self._neighbors()
        n_actions = self.env.max_actions

        # resetear máscara
        self.action_mask[:] = False

        # obtener objetivos actuales
        remaining_wps = getattr(self.env, "remaining_waypoints", [])
        destination = getattr(self.env, "destination", None)

        # target actual: waypoint o destino
        if remaining_wps:
            target = remaining_wps[0]
        else:
            target = destination

        # distancia desde nodo actual
        cur = self.env.current_node
        if self._distances:
            prev_dist = self._distances.get(cur, {}).get(target, np.inf)
        else:
            prev_dist = self._sp_length_cached(cur, target)

        # evaluar cada vecino
        for i, nb in enumerate(neighbors[:n_actions]):
            # bloquear si está en ciclo reciente
            if nb in self.recent_nodes_set:
                continue

            # siempre permitir waypoint o destino directos
            if nb in remaining_wps or (not remaining_wps and nb == destination):
                self.action_mask[i] = True
                continue

            # calcular distancia del vecino al target
            if self._distances:
                nd = self._distances.get(nb, {}).get(target, np.inf)
            else:
                nd = self._sp_length_cached(nb, target)

            # permitir si no aleja
            if nd < prev_dist:
                self.action_mask[i] = True

        # fallback: permitir algo si nada es válido
        if not np.any(self.action_mask) and neighbors:
            self.action_mask[: len(neighbors)] = True

    def _sp_length_cached(self, a, b):
        # obtener distancia con caching
        key = (a, b)
        if key in self._sp_cache:
            return self._sp_cache[key]
        d = self.env._sp_length(a, b)
        if len(self._sp_cache) > self._sp_cache_max:
            self._sp_cache.clear()
        self._sp_cache[key] = d
        return d

    def _update_cycle_tracking(self):
        # actualizar registro de nodos visitados
        self.recent_nodes.append(self.env.current_node)
        self.recent_nodes_set = set(self.recent_nodes)
        self.visit_counter[self.env.current_node] += 1

    def _calculate_cycle_penalty(self):
        # penalización ligera por revisitar nodos
        visit_count = self.visit_counter[self.env.current_node]
        base = getattr(self.env, "anti_loop_penalty", 2.0)
        if visit_count > 2:
            raw = -base * (visit_count - 2)
        else:
            raw = 0.0
        return float(max(raw, -50.0))

    def _initialize_cycle_tracking(self):
        self.recent_nodes = deque([self.env.current_node], maxlen=10)
        self.recent_nodes_set = {self.env.current_node}
        self.visit_counter = defaultdict(int)
        self.visit_counter[self.env.current_node] = 1

    def step(self, action):
        # actualizar máscara y ejecutar acción
        self._update_action_mask_with_cycles()

        # reemplazar accion invalida con una válida
        if action >= self.env.max_actions or not self.action_mask[action]:
            valids = np.where(self.action_mask)[0]
            if len(valids) > 0:
                action = int(np.random.choice(valids))
            else:
                action = 0

        result = self.env.step(action)

        if len(result) == 4:
            obs, reward, done, info = result
            truncated = False
        else:
            obs, reward, done, truncated, info = result

        # aplicar penalización por ciclos
        self._update_cycle_tracking()
        reward = float(reward) + self._calculate_cycle_penalty()

        info["action_mask"] = self.action_mask.copy()

        if len(result) == 4:
            return obs, reward, done, info
        return obs, reward, done, truncated, info

    def reset(self, **kwargs):
        res = self.env.reset(**kwargs)
        if isinstance(res, tuple):
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
    env_cfg=None,
    rew_cfg=None,
    debug=False,
    distances=None,
    distances_path=None,
    action_masking_cfg=None,
):
    env = WaypointNavigationEnv(
        graph=graph,
        start_node=start_node,
        waypoints=waypoints,
        destination=destination,
        env_cfg=env_cfg or {},
        rew_cfg=rew_cfg or {},
    )

    return ActionMaskingWrapper(
        env,
        debug=debug,
        distances=distances,
        distances_path=distances_path,
        action_masking_cfg=action_masking_cfg,
    )
