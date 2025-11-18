from pathlib import Path
import gymnasium as gym
from gymnasium import spaces
import networkx as nx
import numpy as np
from typing import Dict, Any, List, Optional
from src.utils.embeddings import build_node_embeddings

class WaypointNavigationEnv(gym.Env):
    """
    Entorno de navegación en grafo con waypoints y destino fijo.

    - Acción: índice de vecino válido (action_mask se calcula en wrapper externo).
    - Observación: embeddings de nodos + distancias (3d + 3).
    - Recompensa: combina costo de movimiento, progreso, waypoints y penalizaciones.
    """

    metadata = {"render_modes": ["human"]}
    def __init__(
        self,
        graph: nx.MultiDiGraph,
        start_node: int,
        waypoints: List[int],
        destination: int,
        env_cfg: Dict[str, Any],
        rew_cfg: Dict[str, Any],
    ) -> None:
        super().__init__()

        env_cfg = env_cfg or {}
        rew_cfg = rew_cfg or {}

        if waypoints is None:
            waypoints = []
        elif isinstance(waypoints, (int,str)):
            waypoints = [waypoints]
        else:
            try:
                waypoints = list(waypoints)
            except TypeError:
                waypoints = [waypoints]

        self.graph = graph
        self.start_node = start_node
        self.waypoints = waypoints
        self.destination = destination
        self.env_cfg = env_cfg
        self.rew_cfg = rew_cfg
        self.render_mode = self.env_cfg.get("render_mode", "human")

        # inicializar entorno
        self._init_environment(env_cfg)
        self._init_spaces()
        self._init_reward_params(rew_cfg)
        self._reset_state_vars()

    def _init_environment(self, env_cfg: Dict[str, Any]):
        self.max_steps = (
            max(1, self.graph.number_of_nodes())
            if env_cfg.get("max_steps", "auto") == "auto"
            else env_cfg.get("max_steps")
        )
        self.max_wait_steps = (
            self.max_steps
            if env_cfg.get("max_wait_steps", "auto") == "auto"
            else env_cfg.get("max_wait_steps")
        )

        self.distance_matrix = None
        dm = self.graph.graph.get("distances")
        if dm is not None:
            # matriz de distancias precalculada
            self.distance_matrix = dm
        
        # calcular máximo para normalización
        self.max_distance = self._calculate_max_distance()

    def _init_spaces(self):
        # cargar embeddings y configurar espacios
        self.node_embeddings = build_node_embeddings(self.graph)
        self.embedding_dim = len(next(iter(self.node_embeddings.values()), []))
        self.max_actions = max(dict(self.graph.degree()).values(), default=1)
        obs_dim = 3 * self.embedding_dim + 7 + 2 * self.max_actions

        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(self.max_actions)

    def _init_reward_params(self, rew_cfg: Dict[str, Any]):
        # parámetros de configuración de recompensas
        self.weight_name = rew_cfg.get("weight_name", "travel_time")
        self.anti_loop_penalty = rew_cfg.get("anti_loop_penalty", 20.0)
        self.move_cost_coef = rew_cfg.get("move_cost_coef", 0.01)
        self.progress_coef = rew_cfg.get("progress_coef", 5.0)
        self.waypoint_bonus = rew_cfg.get("waypoint_bonus", 50.0)
        self.destination_bonus = rew_cfg.get("destination_bonus", 200.0)
        self.no_progress_penalty = rew_cfg.get("no_progress_penalty", 2.0)

    def _reset_state_vars(self):
        # inicializar variables de estado del episodio
        self.current_node: Optional[int] = None
        self.remaining_waypoints: List[int] = []
        self.path_history: List[int] = []
        self.steps_taken = 0
        self.total_travel_time = 0.0
        self.optimal_steps_to_destination: Optional[int] = None
        self.optimal_steps_to_waypoints: Dict[int, int] = {}


    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        super().reset(seed=seed)
        self.current_node = self.start_node
        self.remaining_waypoints = sorted(
            self.waypoints, key=lambda wp: self._sp_length(self.current_node, wp)
        )
        self.path_history = [self.current_node]
        self.steps_taken = 0
        self.total_travel_time = 0.0
        
        # calcular pasos óptimos esperados para tracking de eficiencia
        self._calculate_optimal_steps()

        obs = self._get_obs()
        info = {
            "path": [self.current_node],
            "remaining_waypoints": self.remaining_waypoints.copy(),
            "current_node": self.current_node,
            "optimal_steps_to_destination": self.optimal_steps_to_destination,
        }
        return obs, info

    def step(self, action: int):
        """Ejecuta una acción y actualiza el estado."""
        self.steps_taken += 1
        reward, done, truncated = 0.0, False, False
        info: Dict[str, Any] = {}

        neighbors = self._neighbors(self.current_node)
        if not neighbors:
            truncated = True
            info["terminated_reason"] = "dead_end"
            return self._finalize_step(reward, done, truncated, info)

        next_node = neighbors[action]
        travel_time = self._compute_travel_cost(self.current_node, next_node)
        progress = self._compute_progress(next_node)

        # actualizar estado
        self.current_node = next_node
        self.path_history.append(next_node)
        self.total_travel_time += travel_time

        # calcular recompensa
        reward += self._compute_reward(travel_time, progress)

        # verificar fin del episodio
        done, truncated, extra_info = self._check_termination(progress)
        info.update(extra_info)

        return self._finalize_step(reward, done, truncated, info)

    def _compute_travel_cost(self, current: int, next_node: int) -> float:
        edge_data = self._edge_data(current, next_node)
        return float(edge_data.get(self.weight_name, edge_data.get("length", 1.0)))

    def _compute_progress(self, next_node: int) -> float:
        # determinar target actual (waypoint o destino)
        if self.remaining_waypoints:
            target = self.remaining_waypoints[0]
        else:
            target = self.destination
        dist_prev = self._sp_length(self.current_node, target)
        dist_curr = self._sp_length(next_node, target)
        return dist_prev - dist_curr

    def _compute_reward(self, travel_time: float, progress: float) -> float:
        # normalizar por distancia máxima
        denom = self.max_distance if self.max_distance > 0 else 1.0
        reward = 0.0

        # recompensa por avance hacia el objetivo
        if progress > 0:
            reward += (progress / denom) * 5.0
        else:
            reward -= 0.05

        # penalización leve por distancia viajada
        reward -= (travel_time / denom) * 0.01

        # bonus por alcanzar waypoint
        if self.current_node in self.remaining_waypoints:
            self.remaining_waypoints.remove(self.current_node)
            reward += self.waypoint_bonus

        # bonus por llegar al destino final
        if self.current_node == self.destination and not self.remaining_waypoints:
            reward += self.destination_bonus

        return float(reward)

    def _check_termination(self, progress: float):
        done = (self.current_node == self.destination) and (len(self.remaining_waypoints) == 0)
        truncated = False
        reason = None

        if done:
            reason = "destination_reached"
        elif self.steps_taken >= self.max_steps:
            truncated, done, reason = True, True, "max_steps"
        elif self.max_wait_steps and self.steps_taken >= self.max_wait_steps:
            truncated, done, reason = True, True, "max_wait_steps"

        info = {"terminated_reason": reason} if reason else {}
        return done, truncated, info

    def _finalize_step(self, reward, done, truncated, info):
        """Genera la observación e info de salida."""
        obs = self._get_obs()
        info.update({
            "path": self.path_history.copy(),
            "remaining_waypoints": list(self.remaining_waypoints),
            "current_node": self.current_node,
            "travel_time": self.total_travel_time,
        })
        return obs, float(reward), done, truncated, info

    def _neighbors(self, node: Optional[int]) -> List[int]:
        return list(self.graph.neighbors(node)) if node in self.graph else []

    def _sp_length(self, a: int, b: int) -> float:
        """Calculates the path using the configured algorithm."""
        if self.distance_matrix is not None:
            try:
                # quick try: direct dict lookup
                return float(self.distance_matrix.get(a, {}).get(b, np.inf))
            except Exception:
                pass

        algorithm = self.env_cfg.get("shortest_path_algorithm", "astar")
        try:
            if algorithm == "astar":
                return float(nx.astar_path_length(
                    self.graph, 
                    a, 
                    b, 
                    heuristic=self._heuristic
                ))
            elif algorithm == "dijkstra":
                return float(nx.shortest_path_length(
                    self.graph, 
                    a, 
                    b, 
                    weight=self.weight_name
                ))
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
        except nx.NetworkXNoPath:
            return float(self.graph.number_of_nodes())
        
    def _heuristic(self, u: int, v: int) -> float:
        """Euclidian heuristic for A* https://www.geeksforgeeks.org/dsa/a-search-algorithm/"""
        u_data = self.graph.nodes[u]
        v_data = self.graph.nodes[v]
        # La distancia euclidiana entre dos puntos es la longitud del segmento de línea entre ellos. Se puede calcular a partir de las coordenadas cartesianas de los puntos utilizando el teorema de Pitágoras.
        return ((u_data['x'] - v_data['x'])**2 + (u_data['y'] - v_data['y'])**2)**0.5
    
    def _calculate_max_distance(self) -> float:
        if self.distance_matrix is not None:
            try:
                max_dist = 0.0
                for source_dict in self.distance_matrix.values():
                    if isinstance(source_dict, dict):
                        for dist in source_dict.values():
                            if isinstance(dist, (int, float)) and dist != np.inf:
                                max_dist = max(max_dist, float(dist))
                if max_dist > 0:
                    return max_dist
            except Exception:
                pass
        
        nodes = list(self.graph.nodes(data=True))
        if len(nodes) < 2:
            return 1.0
        
        max_dist = 0.0
        for i, (u, u_data) in enumerate(nodes):
            ux = float(u_data.get("x", 0.0))
            uy = float(u_data.get("y", 0.0))
            for v, v_data in nodes[i+1:]:
                vx = float(v_data.get("x", 0.0))
                vy = float(v_data.get("y", 0.0))
                dist = ((ux - vx)**2 + (uy - vy)**2)**0.5
                max_dist = max(max_dist, dist)
        
        return max_dist if max_dist > 0 else 1.0
        
    # devuelve un diccionario con la información de la arista entre dos nodos
    def _edge_data(self, u: int, v: int) -> Dict[str, Any]:
        data = self.graph.get_edge_data(u, v, default={})
        if isinstance(data, dict) and all(isinstance(k, int) for k in data.keys()):
            if data:
                entry = data.get(next(iter(data)), {})
                return entry if isinstance(entry, dict) else {}
        return data if isinstance(data, dict) else {}

    def _get_obs(self) -> np.ndarray:
        cur_emb = self._emb(self.current_node)
        dest_emb = self._emb(self.destination)

        if self.remaining_waypoints:
            wp_node = self.remaining_waypoints[0]
            wp_emb = self._emb(wp_node)
            dist_wp = float(self._sp_length(self.current_node, wp_node))
        else:
            wp_node = None
            wp_emb = np.zeros(self.embedding_dim, dtype=np.float32)
            dist_wp = 0.0

        dist_dest = float(self._sp_length(self.current_node, self.destination))

        denom = self.max_distance if self.max_distance > 0 else 1.0
        dist_dest_norm = dist_dest / denom
        dist_wp_norm = dist_wp / denom

        efficiency_info = self._get_efficiency_info()
        scalar_feats = np.array(
            [
                dist_dest_norm,
                dist_wp_norm,
                self.steps_taken / self.max_steps,
                efficiency_info["wp_efficiency"],
                efficiency_info["dest_efficiency"],
                efficiency_info["steps_vs_optimal_wp"],
                efficiency_info["steps_vs_optimal_dest"],
            ],
            dtype=np.float32,
        )

        neighbors = list(self.graph.neighbors(self.current_node))
        neigh_dist_dest = np.zeros(self.max_actions, dtype=np.float32)
        neigh_dist_wp = np.zeros(self.max_actions, dtype=np.float32)

        for i, nb in enumerate(neighbors[: self.max_actions]):
            d_dest = float(self._sp_length(nb, self.destination))
            neigh_dist_dest[i] = d_dest / denom

            if wp_node is not None:
                d_wp = float(self._sp_length(nb, wp_node))
                neigh_dist_wp[i] = d_wp / denom
            else:
                neigh_dist_wp[i] = 0.0

        obs = np.concatenate(
            [
                cur_emb,
                dest_emb,
                wp_emb,
                scalar_feats,
                neigh_dist_dest,
                neigh_dist_wp,
            ]
        ).astype(np.float32)

        return obs


    def _calculate_optimal_steps(self):
        # calcular distancias óptimas para comparación
        self.optimal_steps_to_waypoints = {}
        current = self.current_node if self.current_node is not None else self.start_node
        
        for wp in self.waypoints:
            if wp in self.graph.nodes:
                sp_dist = self._sp_length(current, wp)
                self.optimal_steps_to_waypoints[wp] = max(1, int(sp_dist))
                current = wp
        
        if self.destination in self.graph.nodes:
            if self.waypoints:
                last_wp = self.waypoints[-1]
                sp_dist = self._sp_length(last_wp, self.destination)
            else:
                sp_dist = self._sp_length(self.start_node, self.destination)
            self.optimal_steps_to_destination = max(1, int(sp_dist))

    def _get_efficiency_info(self) -> Dict[str, float]:
        # calcular métricas de eficiencia vs ruta óptima
        info = {
            'wp_efficiency': 0.0,
            'dest_efficiency': 0.0,
            'steps_vs_optimal_wp': 0.0,
            'steps_vs_optimal_dest': 0.0,
        }
        
        # eficiencia hacia waypoint pendiente
        if self.remaining_waypoints:
            wp_node = self.remaining_waypoints[0]
            if wp_node in self.optimal_steps_to_waypoints:
                optimal_steps = self.optimal_steps_to_waypoints[wp_node]
                if optimal_steps > 0:
                    # eficiencia: 1.0 si está en camino óptimo, <1.0 si va más lento
                    # usar distancia restante como aproximación de pasos restantes
                    dist_remaining = self._sp_length(self.current_node, wp_node)
                    estimated_total_steps = self.steps_taken + dist_remaining
                    info['steps_vs_optimal_wp'] = estimated_total_steps / max(optimal_steps, 1.0)
                    # eficiencia: inversa del ratio (1.0 = óptimo, <1.0 = peor)
                    info['wp_efficiency'] = min(1.0, optimal_steps / max(estimated_total_steps, 1.0))
        
        # eficiencia hacia destino
        if self.optimal_steps_to_destination is not None:
            optimal_steps = self.optimal_steps_to_destination
            if optimal_steps > 0:
                dist_remaining = self._sp_length(self.current_node, self.destination)
                estimated_total_steps = self.steps_taken + dist_remaining
                info['steps_vs_optimal_dest'] = estimated_total_steps / max(optimal_steps, 1.0)
                # Eficiencia: inversa del ratio (1.0 = óptimo, <1.0 = peor)
                info['dest_efficiency'] = min(1.0, optimal_steps / max(estimated_total_steps, 1.0))
        
        return info

    def _emb(self, node: Optional[int]) -> np.ndarray:
        if node is None or self.embedding_dim == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        vec = self.node_embeddings.get(str(node))
        return np.asarray(vec, dtype=np.float32) if vec is not None else np.zeros(self.embedding_dim, dtype=np.float32)

