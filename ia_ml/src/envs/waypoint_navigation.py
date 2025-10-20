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

    def __init__(self, graph: nx.Graph, waypoints: list, destination: int, render_mode=None):
        super().__init__()

        self.graph = graph
        self.waypoints = waypoints.copy()
        self.destination = destination
        self.current_node = None
        self.remaining_waypoints = []

        # Observation Space https://gymnasium.farama.org/api/spaces/
        # Observation vector = [current_node, current_waypoint, destination]
        self.observation_space = spaces.Box(low=0, high=len(graph.nodes),
                                            shape=(3,), dtype=np.int32)

        # Compute maximum node degree once to define a fixed-size action space
        # and to build action masks for valid neighbor choices at each step.
        degrees = dict(self.graph.degree())
        self._max_degree = max(degrees.values()) if degrees else 1

        # Action = choose neighbor (index into sorted neighbors list)
        self.action_space = spaces.Discrete(self._max_degree)

        # Store render_mode to avoid unused-argument warning
        self.render_mode = render_mode

    def reset(self, *, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed, options=options)
        self.current_node = self.np_random.integers(
            low=0, high=len(self.graph.nodes))
        self.remaining_waypoints = self.waypoints.copy()

        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination], dtype=np.int32)

        # Provide an action mask to help mask-aware algorithms/losses
        info = {"action_mask": self._build_action_mask(self.current_node)}
        return obs, info

    def step(self, action):
        """Execute one step in the environment."""
        # Use a stable neighbor ordering so action indices are consistent
        neighbors = sorted(list(self.graph.neighbors(self.current_node)))

        if action >= len(neighbors):
            # Wrong action -> penlty
            reward = -10
            done = False
        else:
            # Move to the neighbor
            self.current_node = neighbors[action]
            reward = -1
            done = False

            # Check if reach waypoint
            if self.remaining_waypoints and self.current_node == self.remaining_waypoints[0]:
                reward = +100
                self.remaining_waypoints.pop(0)

            # Check if reach destination
            if not self.remaining_waypoints and self.current_node == self.destination:
                reward = +1000
                done = True

        obs = np.array([
            self.current_node,
            self.remaining_waypoints[0] if self.remaining_waypoints else self.destination,
            self.destination], dtype=np.int32)

        info = {"action_mask": self._build_action_mask(self.current_node)}
        return obs, reward, done, False, info

    def render(self):
        """Render the current state of the environment."""
        print(f"Current node: {self.current_node}, "
              f"Remaining waypoints: {self.remaining_waypoints}")

    # ---- Helpers ----
    def _build_action_mask(self, node_id: int) -> np.ndarray:
        """Return a boolean mask of length max_degree marking valid neighbor actions.

        True entries in [0:deg) indicate valid neighbor indices given the current
        sorted neighbor list. Remaining entries are False (invalid/padded actions).
        """
        deg = self.graph.degree(node_id)
        mask = np.zeros(self._max_degree, dtype=bool)
        mask[:deg] = True
        return mask
