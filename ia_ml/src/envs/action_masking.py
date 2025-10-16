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
    Wrapper para implementar action masking y prevención de ciclos.
    
    Características:
    - Filtra automáticamente acciones inválidas
    - Previene ciclos usando una cola de nodos recientes
    - Aplica penalizaciones por comportamiento cíclico
    - Mantiene contadores de visitas por nodo
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.env = env
        # cola de 10 nodos para prevenir ciclos
        self.recent_nodes = deque(maxlen=10)
        self.visit_counter = defaultdict(int)
        # crear nuestra propia máscara de acciones
        self.action_mask = np.zeros(self.env.max_actions, dtype=bool)
        
    def _update_action_mask_with_cycles(self):
        """Actualiza la máscara considerando nodos recientes para prevenir ciclos."""
        neighbors = list(self.env.graph.neighbors(self.env.current_node))
        
        # Inicializar máscara como False (todas inválidas por defecto)
        self.action_mask.fill(False)
        
        # Marcar como válidas solo las acciones que van a vecinos válidos
        # y que no están en la cola de nodos recientes
        for i, neighbor in enumerate(neighbors):
            if i < self.env.max_actions and neighbor not in self.recent_nodes:
                self.action_mask[i] = True
        
        # Si no hay acciones válidas, permitir al menos una para evitar deadlock
        if not np.any(self.action_mask) and neighbors:
            self.action_mask[0] = True
    
    def _get_valid_action_fallback(self):
        """Obtiene una acción válida como fallback cuando la acción original no es válida."""
        valid_actions = np.where(self.action_mask)[0]
        if len(valid_actions) > 0:
            return np.random.choice(valid_actions)
        else:
            return 0  # Fallback a la primera acción disponible
    
    def _update_cycle_tracking(self):
        """Actualiza el seguimiento de nodos visitados para detectar ciclos."""
        self.recent_nodes.append(self.env.current_node)
        self.visit_counter[self.env.current_node] += 1
    
    def _calculate_cycle_penalty(self):
        """Calcula la penalización por ciclos basada en patrones repetitivos."""
        cycle_penalty = 0
        
        # Verificar patrón repetitivo en los últimos 10 nodos
        if len(self.recent_nodes) == 10:
            recent = list(self.recent_nodes)[-5:]
            previous = list(self.recent_nodes)[-10:-5]
            if recent == previous:
                cycle_penalty = -50
        
        # Penalizar por visitas excesivas al mismo nodo
        visit_count = self.visit_counter[self.env.current_node]
        if visit_count > 3:
            cycle_penalty = max(cycle_penalty, -20 * (visit_count - 3))
        
        return cycle_penalty
    
    def _initialize_cycle_tracking(self):
        """Inicializa las variables de seguimiento de ciclos."""
        self.recent_nodes = deque([self.env.current_node], maxlen=10)
        self.visit_counter = defaultdict(int)
        self.visit_counter[self.env.current_node] = 1
        
    def step(self, action):
        """
        Ejecuta un paso con action masking y prevención de ciclos.
        
        Args:
            action: Acción seleccionada por el agente
            
        Returns:
            tuple: (obs, reward, done, truncated, info) con penalizaciones aplicadas
        """
        # Actualizar máscara considerando nodos recientes
        self._update_action_mask_with_cycles()
        
        # Si la acción no es válida, seleccionar una válida aleatoriamente
        if not self.action_mask[action]:
            action = self._get_valid_action_fallback()
        
        # Ejecutar el paso en el entorno base
        obs, reward, done, truncated, info = self.env.step(action)
        
        # Actualizar estado de seguimiento de ciclos
        self._update_cycle_tracking()
        
        # Calcular y aplicar penalizaciones por ciclos
        cycle_penalty = self._calculate_cycle_penalty()
        reward += cycle_penalty
        
        return obs, reward, done, truncated, info
    
    def reset(self, **kwargs):
        """
        Reinicia el entorno y las variables de seguimiento de ciclos.
        
        Args:
            **kwargs: Argumentos adicionales para el reset
            
        Returns:
            tuple: (obs, info) del entorno reiniciado
        """
        obs, info = self.env.reset(**kwargs)
        # Reinicializar variables para detección de ciclos
        self._initialize_cycle_tracking()
        return obs, info
    
    def get_action_mask(self):
        """
        Retorna la máscara de acciones actual.
        
        Returns:
            np.ndarray: Array booleano indicando qué acciones son válidas
        """
        return self.action_mask.copy()
    
    def get_valid_actions(self):
        """
        Retorna las acciones válidas basadas en la máscara.
        
        Returns:
            list: Lista de índices de acciones válidas
        """
        return [i for i, valid in enumerate(self.action_mask) if valid]
    
    @property
    def current_node(self):
        """
        Acceso al nodo actual del entorno envuelto.
        
        Returns:
            int: ID del nodo actual
        """
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
