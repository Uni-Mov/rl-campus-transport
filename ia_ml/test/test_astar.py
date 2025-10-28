import osmnx as ox
from pathlib import Path
import sys

IA_ML_DIR = str(Path(__file__).parent.parent.resolve()) 
if IA_ML_DIR not in sys.path:
    sys.path.insert(0, IA_ML_DIR)

from src.envs.waypoint_navigation import WaypointNavigationEnv

def main():
    city_graph = ox.graph_from_place("Río Cuarto, Córdoba, Argentina", network_type="drive")

    env = WaypointNavigationEnv(
        graph=city_graph,
        start_node=list(city_graph.nodes)[0],  #
        waypoints=[list(city_graph.nodes)[10], list(city_graph.nodes)[20]],  
        destination=list(city_graph.nodes)[30],  
        env_cfg={"shortest_path_algorithm": "astar"},  
        rew_cfg={}
    )

    obs, info = env.reset()
    print("Observación inicial:", obs)
    print("Información inicial:", info)

    done = False
    step_count = 0
    while not done:
        step_count+=1
        print(f"Paso {step_count}")

        neighbors = env._neighbors(env.current_node)
        mask = env._get_action_mask()
        print("\nVecinos disponibles:", neighbors)
        print("Máscara de acciones:", mask)

        action = 0
        obs, reward, done, truncated, info = env.step(action)

        print("Recompensa:", reward)
        print("Nueva observación:", obs)
        print("Información:", info)

        if truncated:
            print("Episodio truncado:", info["terminated_reason"])
            break

        if step_count >= 50:  # Limit to prevent infinite loops
            print("Límite de pasos alcanzado.")
            break

    print("Episodio terminado.")

if __name__ == "__main__":
    main()