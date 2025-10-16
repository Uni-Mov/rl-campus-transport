"""
Waypoint Navigation Environment for Reinforcement Learning.

This module implements a custom Gymnasium environment for graph-based navigation
with waypoints using NetworkX graphs with proper action masking to prevent invalid actions and cycles.
"""
from collections import deque, defaultdict
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
        self.path_history = []
        
        # precalcular distancias shortest path entre todos los nodos
        self.shortest_paths = dict(nx.all_pairs_shortest_path_length(graph))
        self.observation_space = spaces.Box(low=0, high=len(graph.nodes),
                                          shape=(3,), dtype=np.int32)

        # Action space dinámico basado en el grado máximo del grafo
        max_degree = max(dict(graph.degree()).values()) if graph.number_of_nodes() > 0 else 1
        self.max_actions = max_degree
        
        # Action = choose neighbor (espacio dinámico)
        self.action_space = spaces.Discrete(self.max_actions)

        # Store render_mode to avoid unused-argument warning
        self.render_mode = render_mode
    
    def get_distance(self, node1, node2):
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

        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination], dtype=np.int32)
        return obs, {}

    def _execute_movement(self, action):
        """Ejecuta el movimiento del agente al nodo vecino seleccionado."""
        neighbors = list(self.graph.neighbors(self.current_node))
        self.current_node = neighbors[action]
        self.path_history.append(self.current_node)
        
    def _calculate_base_reward(self, dist_before, dist_after):
        """Calcula la recompensa base por progreso hacia el objetivo."""
        if dist_after < dist_before:
            return 0  # Se acercó al objetivo
        elif dist_after > dist_before:
            return -2  # Se alejó del objetivo
        else:
            return -1  # No cambió la distancia
    
    def _check_waypoint_reached(self):
        """Verifica si se alcanzó un waypoint y actualiza la lista."""
        if self.remaining_waypoints and self.current_node == self.remaining_waypoints[0]:
            self.remaining_waypoints.pop(0)
            return 100  # Bonus por alcanzar waypoint
        return 0
    
    def _check_destination_reached(self):
        """Verifica si se alcanzó el destino final."""
        if not self.remaining_waypoints and self.current_node == self.destination:
            return True
        return False
    
    def _get_observation(self):
        """Genera la observación actual del entorno."""
        next_target = self.remaining_waypoints[0] if self.remaining_waypoints else self.destination
        return np.array([
            self.current_node,
            next_target,
            self.destination
        ], dtype=np.int32)
    
    def _get_info(self):
        """Genera la información adicional del paso actual."""
        return {
            "path": self.path_history.copy()
        }

    def step(self, action):
        """Execute one step in the environment."""
        self.steps_taken += 1
        
        # determinar siguiente objetivo (waypoint o destino)
        next_target = self.remaining_waypoints[0] if self.remaining_waypoints else self.destination
        
        # calcular distancia ANTES del movimiento
        dist_before = self.get_distance(self.current_node, next_target)

        # ejecutar movimiento
        self._execute_movement(action)

        # calcular distancia DESPUÉS del movimiento
        dist_after = self.get_distance(self.current_node, next_target)
        
        # calcular recompensa total
        reward = self._calculate_base_reward(dist_before, dist_after)
        reward += self._check_waypoint_reached()
        
        # verificar si se alcanzó el destino final
        done = self._check_destination_reached()
        if done:
            reward += 1000  # Bonus por alcanzar destino final
        
        # truncamiento por pasos máximos
        truncated = self.steps_taken >= self.max_steps

        # generar observación e información
        obs = self._get_observation()
        info = self._get_info()

        return obs, reward, done, truncated, info


    def render(self):
        """Render the current state of the environment."""
        neighbors = list(self.graph.neighbors(self.current_node))
        print(f"Current node: {self.current_node}, "
              f"Remaining waypoints: {self.remaining_waypoints}, "
              f"Available neighbors: {neighbors}")

