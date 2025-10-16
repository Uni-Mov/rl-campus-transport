# ...existing code...
# Expose WaypointNavigationEnv for easier imports
from .waypoint_navigation import WaypointNavigationEnv
from .action_masking import ActionMaskingWrapper, create_masked_waypoint_env

__all__ = ["WaypointNavigationEnv", "ActionMaskingWrapper", "create_masked_waypoint_env"]