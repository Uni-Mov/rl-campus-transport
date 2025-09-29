from gymnasium.envs.registration import register

# Registering the environment so that it can be imported as a module later
register(
    id="WaypointNavigationEnv-v0",  #Environment name
    entry_point="envs.waypoint_navigation:WaypointNavigation",  # Environment path
)
