"""
Waypoint Navigation Environment for Reinforcement Learning.

This module implements a custom Gymnasium environment for graph-based navigation
with waypoints using NetworkX graphs.
"""
import gymnasium as gym
from gymnasium import spaces
import networkx as nx
import numpy as np


class WaypointNavigationEnv(gym.Env):
    """
    
    RL environment for graph navigation:
    - State: current node + waypoint/s + final destination
    - Action: Choose a neighbor
    - Reward: Penalty for steps, reward for reach waypoint/destination
    """
    meta = {"render_modes": ["human"]}  # Supported render modes

    def __init__(self, graph: nx.Graph, waypoints: list, destination: int, 
                 max_steps=20, render_mode=None):
        super().__init__()

        self.graph = graph
        self.waypoints = waypoints.copy()
        self.destination = destination
        self.max_steps = max_steps
        self.current_node = None
        self.remaining_waypoints = []
        self.steps_taken = 0
        
        # guardar camino tomado
        self.path_history = []
        
        # variables para detección de ciclos
        self.recent_nodes = []
        self.visit_counter = {}
        
        # precalcular distancias shortest path entre todos los nodos
        self.shortest_paths = dict(nx.all_pairs_shortest_path_length(graph))

        # Observation Space https://gymnasium.farama.org/api/spaces/
        # Observation vector= [current_node, current_waypoint, destination]
        self.observation_space = spaces.Box(low=0, high=len(graph.nodes),
                                          shape=(3,), dtype=np.int32)

        # Action = choose neighbor
        self.action_space = spaces.Discrete(10)

        # Store render_mode to avoid unused-argument warning
        self.render_mode = render_mode
    
    def _get_distance(self, node1, node2):
        """
        obtiene la distancia shortest path entre dos nodos.
        
        parametros:
            node1: nodo origen
            node2: nodo destino
            
        retorna:
            int: numero de pasos del camino mas corto
        """
        try:
            return self.shortest_paths[node1][node2]
        except KeyError:
            # si no hay camino, retornar distancia muy grande
            return len(self.graph.nodes)

    def reset(self, *, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed, options=options)
        self.current_node = 0
        self.remaining_waypoints = self.waypoints.copy()
        self.steps_taken = 0
        
        # inicializar historial con nodo de inicio
        self.path_history = [self.current_node]
        
        # reinicializar variables para detección de ciclos
        self.recent_nodes = [self.current_node]
        self.visit_counter = {self.current_node: 1}

        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination], dtype=np.int32)
        return obs, {}

    def step(self, action):
        """Execute one step in the environment."""
        self.steps_taken += 1
        neighbors = list(self.graph.neighbors(self.current_node))
        
        # determinar siguiente objetivo (waypoint o destino)
        next_target = self.remaining_waypoints[0] if self.remaining_waypoints else self.destination
        
        # calcular distancia ANTES del movimiento
        dist_before = self._get_distance(self.current_node, next_target)

        # acción inválida
        if action >= len(neighbors):
            reward = -10
            done = False
            truncated = self.steps_taken >= self.max_steps
            obs = np.array([
                self.current_node,
                next_target,
                self.destination
            ], dtype=np.int32)
            info = {"path": self.path_history.copy()}
            return obs, reward, done, truncated, info

        # mover al vecino seleccionado
        self.current_node = neighbors[action]
        self.path_history.append(self.current_node)

        # actualizar ventana y contador para penalizaciones
        self.recent_nodes.append(self.current_node)
        self.visit_counter[self.current_node] += 1

        # calcular penalizaciones por ciclos
        cycle_penalty = 0
        if len(self.recent_nodes) == 6:
            recent = list(self.recent_nodes)[-3:]
            previous = list(self.recent_nodes)[:3]
            if recent == previous:
                cycle_penalty = -50

        visit_count = self.visit_counter[self.current_node]
        if visit_count > 3:
            cycle_penalty = max(cycle_penalty, -20 * (visit_count - 3))

        # calcular distancia DESPUÉS del movimiento y recompensa base
        dist_after = self._get_distance(self.current_node, next_target)
        if dist_after < dist_before:
            reward = 0
        elif dist_after > dist_before:
            reward = -2
        else:
            reward = -1

        reward += cycle_penalty

        # bonus por alcanzar waypoint
        if self.remaining_waypoints and self.current_node == self.remaining_waypoints[0]:
            reward = 100
            self.remaining_waypoints.pop(0)

        # bonus por alcanzar destino final
        done = False
        if not self.remaining_waypoints and self.current_node == self.destination:
            reward = 1000
            done = True

        # truncamiento por pasos máximos
        truncated = self.steps_taken >= self.max_steps

        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination
        ], dtype=np.int32)

        info = {"path": self.path_history.copy()}

        return obs, reward, done, truncated, info

    def render(self):
        """Render the current state of the environment."""
        print(f"Current node: {self.current_node}, "
              f"Remaining waypoints: {self.remaining_waypoints}")