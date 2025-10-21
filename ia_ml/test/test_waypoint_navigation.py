import pytest
from src.envs.waypoint_navigation import WaypointNavigationEnv

def test_environment_initialization(city_graph):
    env = WaypointNavigationEnv(
        graph=city_graph,
        start_node=list(city_graph.nodes)[0],
        waypoints=[list(city_graph.nodes)[10], list(city_graph.nodes)[20]],
        destination=list(city_graph.nodes)[30], 
        env_cfg={"render_mode": "human"},
        rew_cfg={}
    )
    obs, info = env.reset()
    assert env.current_node == list(city_graph.nodes)[0]
    assert env.destination == list(city_graph.nodes)[30]
    assert len(env.remaining_waypoints) == 2

def test_action_mask(city_graph):
    env = WaypointNavigationEnv(
        graph=city_graph,
        start_node=list(city_graph.nodes)[0],
        waypoints=[list(city_graph.nodes)[10], list(city_graph.nodes)[20]],
        destination=list(city_graph.nodes)[30],
        env_cfg={},
        rew_cfg={}
    )
    env.reset()
    mask = env._get_action_mask()
    assert mask.sum() > 0 

def test_reward_calculation(city_graph):
    env = WaypointNavigationEnv(
        graph=city_graph,
        start_node=list(city_graph.nodes)[0],
        waypoints=[list(city_graph.nodes)[10]],
        destination=list(city_graph.nodes)[30],
        env_cfg={},
        rew_cfg={"progress_coef": 5.0, "waypoint_bonus": 50.0}
    )
    env.reset()
    _, reward, _, _, _ = env.step(0)
    assert reward != 0  