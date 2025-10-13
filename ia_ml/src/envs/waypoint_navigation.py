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
        self.current_node = self.np_random.integers(
            low=0, high=len(self.graph.nodes))
        self.remaining_waypoints = self.waypoints.copy()
        self.steps_taken = 0
        
        # inicializar historial con nodo de inicio
        self.path_history = [self.current_node]

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
        next_target = (self.remaining_waypoints[0] if self.remaining_waypoints 
                      else self.destination)
        
        # calcular distancia ANTES del movimiento
        dist_before = self._get_distance(self.current_node, next_target)

        if action >= len(neighbors):
            # accion invalida -> penalizacion fuerte
            reward = -10
            done = False
            truncated = self.steps_taken >= self.max_steps
            
            obs = np.array([
                self.current_node,
                self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
                self.destination], dtype=np.int32)
            
            return obs, reward, done, truncated, {"path": self.path_history.copy()}
        else:
            # mover al vecino seleccionado
            self.current_node = neighbors[action]
            self.path_history.append(self.current_node)
            
            # calcular distancia despues del movimiento
            dist_after = self._get_distance(self.current_node, next_target)
           
            # comparar distancias para saber si progresamos
            if dist_after < dist_before:
                # nos acercamos: distancia disminuyo
                # dar recompensa neutral (0) porque vamos bien
                reward = 0
            elif dist_after > dist_before:
                # penalizacion por ir en direccion incorrecta
                reward = -2
            else:
                # misma distancia: no progresamos ni retrocedimos
                reward = -1
            
            # detectar ciclo
            cycle_penalty = 0
            
            #  ventana deslizante
            if len(self.path_history) >= 6:
                recent = self.path_history[-3:]
                previous = self.path_history[-6:-3]
                if recent == previous:
                    cycle_penalty = -50
            
            # contador de visitas
            visit_count = self.path_history.count(self.current_node)
            if visit_count > 3:
                cycle_penalty = -20 * (visit_count - 3)
            
            reward += cycle_penalty
            
            done = False

            # bonus por alcanzar waypoint
            if self.remaining_waypoints and self.current_node == self.remaining_waypoints[0]:
                reward = +100
                self.remaining_waypoints.pop(0)

            # bonus grande por alcanzar destino
            if not self.remaining_waypoints and self.current_node == self.destination:
                reward = +1000
                done = True

        # verificar truncation (limite de pasos)
        truncated = self.steps_taken >= self.max_steps
        
        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination], dtype=np.int32)
        
        # retornar camino en info para poder accederlo
        info = {"path": self.path_history.copy()}

        return obs, reward, done, truncated, info

    def render(self):
        """Render the current state of the environment."""
        print(f"Current node: {self.current_node}, "
              f"Remaining waypoints: {self.remaining_waypoints}")