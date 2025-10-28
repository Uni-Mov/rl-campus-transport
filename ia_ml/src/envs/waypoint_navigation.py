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

        # inicialización de entorno
        self._init_environment(env_cfg)
        self._init_spaces()
        self._init_reward_params(rew_cfg)
        self._reset_state_vars()

    # configuracion de entorno
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

    # espacios de accion y observacion
    def _init_spaces(self):
        self.node_embeddings = build_node_embeddings(self.graph)
        self.embedding_dim = len(next(iter(self.node_embeddings.values()), []))
        obs_dim = 3 * self.embedding_dim + 3

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        self.max_actions = max(dict(self.graph.degree()).values(), default=1)
        self.action_space = spaces.Discrete(self.max_actions)

    # parametros de recompensa
    def _init_reward_params(self, rew_cfg: Dict[str, Any]):
        self.weight_name = rew_cfg.get("weight_name", "travel_time")
        self.anti_loop_penalty = rew_cfg.get("anti_loop_penalty", 20.0)
        self.move_cost_coef = rew_cfg.get("move_cost_coef", 0.01)
        self.progress_coef = rew_cfg.get("progress_coef", 5.0)
        self.waypoint_bonus = rew_cfg.get("waypoint_bonus", 50.0)
        self.destination_bonus = rew_cfg.get("destination_bonus", 200.0)
        self.no_progress_penalty = rew_cfg.get("no_progress_penalty", 2.0)

    # variables de estado
    def _reset_state_vars(self):
        self.current_node: Optional[int] = None
        self.remaining_waypoints: List[int] = []
        self.visited_waypoints: set[int] = set()
        self.path_history: List[int] = []
        self.steps_taken = 0
        self.total_travel_time = 0.0


    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        super().reset(seed=seed)
        self.current_node = self.start_node
        self.remaining_waypoints = sorted(
            self.waypoints, key=lambda wp: self._sp_length(self.current_node, wp)
        )
        self.visited_waypoints.clear()
        self.path_history = [self.current_node]
        self.steps_taken = 0
        self.total_travel_time = 0.0

        obs = self._get_obs()
        info = {
            "path": [self.current_node],
            "remaining_waypoints": self.remaining_waypoints.copy(),
            "current_node": self.current_node,
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

        # recompensa principal
        reward += self._compute_reward(travel_time, progress)

        # condiciones de fin
        done, truncated, extra_info = self._check_termination(progress)
        info.update(extra_info)

        return self._finalize_step(reward, done, truncated, info)

    def _compute_travel_cost(self, current: int, next_node: int) -> float:
        edge_data = self._edge_data(current, next_node)
        return float(edge_data.get(self.weight_name, edge_data.get("length", 1.0)))

    def _compute_progress(self, next_node: int) -> float:
        dist_prev = self._sp_length(self.current_node, self.destination)
        dist_curr = self._sp_length(next_node, self.destination)
        return dist_prev - dist_curr

    def _compute_reward(self, travel_time: float, progress: float) -> float:
        reward = 0.0
        reward -= self.move_cost_coef * travel_time
        reward += self.progress_coef * progress

        # waypoint alcanzado
        if self.current_node in self.remaining_waypoints:
            self.remaining_waypoints.remove(self.current_node)
            self.visited_waypoints.add(self.current_node)
            reward += self.waypoint_bonus

        # destino alcanzado
        if self.current_node == self.destination:
            reward += self.destination_bonus

        # penalizaciones
        if self.path_history.count(self.current_node) > 2:
            reward -= self.anti_loop_penalty
        if progress <= 0:
            reward -= self.no_progress_penalty

        return reward

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


    # funciones auxiliares para el grafo
    def _neighbors(self, node: Optional[int]) -> List[int]:
        return list(self.graph.neighbors(node)) if node in self.graph else []
    
    #Getter de la mascara de acciones válidas, ahora es dinamica
    def _get_action_mask(self) -> np.ndarray:
        mask = np.zeros(self.max_actions, dtype=bool)
        neighbors = self._neighbors(self.current_node)
        valid_indices = range(len(neighbors))
        mask[list(valid_indices)] = True
        return mask

    def _sp_length(self, a: int, b: int) -> float:
        """Calculates the path using the configured algorithm."""
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
        
    # devuelve un diccionario con la información de la arista entre dos nodos
    def _edge_data(self, u: int, v: int) -> Dict[str, Any]:
        data = self.graph.get_edge_data(u, v, default={})
        if isinstance(data, dict) and all(isinstance(k, int) for k in data.keys()):
            if data:
                entry = data.get(next(iter(data)), {})
                return entry if isinstance(entry, dict) else {}
        return data if isinstance(data, dict) else {}

    def _get_obs(self) -> np.ndarray:
    # embeddings del nodo actual y del destino
        cur_emb = self._emb(self.current_node)
        dest_emb = self._emb(self.destination)

    # si hay waypoints pendientes
        if self.remaining_waypoints:
            wp_node = self.remaining_waypoints[0]
            wp_emb = self._emb(wp_node)
            dist_wp = float(self._sp_length(self.current_node, wp_node))
        else:
            # distancia al siguiente waypoint = 0, ya no hay mas, solo se encarga del destino
            wp_emb = np.zeros(self.embedding_dim, dtype=np.float32)
            dist_wp = 0.0

    # distancia al destino y progreso normalizado
        dist_dest = float(self._sp_length(self.current_node, self.destination))
        scalar_feats = np.array(
            [dist_dest, dist_wp, self.steps_taken / self.max_steps],
            dtype=np.float32,
        )

    # vector de observación final
    # que tan lejos está del destino,
    # que tan lejos está del siguiente objetivo intermedio,
    # cuanto le queda antes de que el episodio termine.
        return np.concatenate([cur_emb, dest_emb, wp_emb, scalar_feats]).astype(np.float32)


    def _emb(self, node: Optional[int]) -> np.ndarray:
        if node is None or self.embedding_dim == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        vec = self.node_embeddings.get(str(node))
        return np.asarray(vec, dtype=np.float32) if vec is not None else np.zeros(self.embedding_dim, dtype=np.float32)
