"""
Action Masking Wrapper for Waypoint Navigation Environment.

This module provides action masking functionality to prevent invalid actions
and cycles in the waypoint navigation environment.
"""
from collections import deque, defaultdict
import gymnasium as gym
import numpy as np


class ActionMaskingWrapper(gym.Wrapper):
    """
    Wrapper personalizado para implementar masking real de acciones.
    Filtra las acciones inválidas y previene ciclos usando una cola de 10 nodos.
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.env = env
        # cola de 10 nodos para prevenir ciclos
        self.recent_nodes = deque(maxlen=10)
        self.visit_counter = defaultdict(int)
        
    def _update_action_mask_with_cycles(self):
        """Actualiza la máscara considerando nodos recientes para prevenir ciclos."""
        neighbors = list(self.env.graph.neighbors(self.env.current_node))
        
        # inicializar máscara como False
        self.env.action_mask.fill(False)
        
        # marcar como válidas solo las acciones que van a vecinos válidos
        # y que no están en la cola de nodos recientes
        for i, neighbor in enumerate(neighbors):
            if i < self.env.max_actions:  # Solo considerar las acciones disponibles
                # verificar si el vecino no está en la cola de nodos recientes
                if neighbor not in self.recent_nodes:
                    self.env.action_mask[i] = True
        
        # si no hay acciones válidas (todos los vecinos están en la cola reciente),
        # permitir al menos una acción para evitar deadlock
        if not np.any(self.env.action_mask) and neighbors:
            # permitir la primera acción disponible
            self.env.action_mask[0] = True
        
    def step(self, action):
        """Ejecuta un paso con masking real y prevención de ciclos."""
        # actualizar máscara considerando nodos recientes
        self._update_action_mask_with_cycles()
        
        # si la acción no es válida, seleccionar una valida aleatoriamente
        if not self.env.action_mask[action]:
            valid_actions = np.where(self.env.action_mask)[0]
            if len(valid_actions) > 0:
                action = np.random.choice(valid_actions)
            else:
                # si no hay acciones válidas, usar la primera disponible
                action = 0
        
        # ejecutar el paso
        obs, reward, done, truncated, info = self.env.step(action)
        
        # actualizar cola de nodos recientes
        self.recent_nodes.append(self.env.current_node)
        self.visit_counter[self.env.current_node] += 1
        
        # calcular penalizaciones por ciclos
        cycle_penalty = 0
        if len(self.recent_nodes) == 10:
            # verificar si hay un patron repetitivo en los ultimos 5 nodos
            recent = list(self.recent_nodes)[-5:]
            previous = list(self.recent_nodes)[-10:-5]
            if recent == previous:
                cycle_penalty = -50

        visit_count = self.visit_counter[self.env.current_node]
        if visit_count > 3:
            cycle_penalty = max(cycle_penalty, -20 * (visit_count - 3))
        
        # aplicar penalizacion por ciclos
        reward += cycle_penalty
        
        return obs, reward, done, truncated, info
    
    def reset(self, **kwargs):
        """Reset con informacion de mascara."""
        obs, info = self.env.reset(**kwargs)
        # reinicializar variables para deteccion de ciclos
        self.recent_nodes = deque([self.env.current_node], maxlen=10)
        self.visit_counter = defaultdict(int)
        self.visit_counter[self.env.current_node] = 1
        return obs, info
    
    def get_action_mask(self):
        """Retorna la mascara de acciones actual."""
        return self.env.get_action_mask()
    
    def get_valid_actions(self):
        """Retorna las acciones validas."""
        return self.env.get_valid_actions()
    
    @property
    def current_node(self):
        """Acceso al nodo actual del entorno envuelto."""
        return self.env.current_node


def create_masked_waypoint_env(graph, waypoints, destination, max_steps=20, render_mode=None):
    """
    Crea un entorno WaypointNavigationEnv con masking real.
    
    Args:
        graph: Grafo de NetworkX
        waypoints: Lista de waypoints
        destination: Nodo destino final
        max_steps: Máximo número de pasos
        render_mode: Modo de renderizado
        
    Returns:
        Env envuelto con ActionMaskingWrapper personalizado
    """
    from .waypoint_navigation import WaypointNavigationEnv
    env = WaypointNavigationEnv(graph, waypoints, destination, max_steps, render_mode)
    return ActionMaskingWrapper(env)
