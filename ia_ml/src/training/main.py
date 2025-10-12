"""
script de entrenamiento para navegacion con waypoints usando ppo.
"""
import networkx as nx
from stable_baselines3 import PPO
import sys
from pathlib import Path

# agregar directorio raiz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from ia_ml.src.envs.waypoint_navigation import WaypointNavigationEnv


def main():
    # crear grafo 
    grid_size = 5
    G = nx.grid_2d_graph(grid_size, grid_size)
    G = nx.convert_node_labels_to_integers(G)
    
    n_nodes = G.number_of_nodes()
    
    # definir waypoints y destino
    waypoints = [int(n_nodes * 0.25), int(n_nodes * 0.75)]
    destination = n_nodes - 1
    
    print(f"grafo: {n_nodes} nodos")
    print(f"waypoints: {waypoints}, destino: {destination}\n")
    
    # crear entorno
    # max_steps: limite de pasos para el episodio, usarlo en proporcion a la cantidad de nodos que haya
    env = WaypointNavigationEnv(G, waypoints, destination, max_steps=15)
    
    # configurar modelo ppo
    # mlppolicy: red neuronal multicapa que recibe estado y devuelve accion
    model = PPO("MlpPolicy", env, verbose=1)
    
    # entrenar
    model.learn(total_timesteps=50_000)
    
    # guardar modelo
    model.save(f"ppo_waypoint_{grid_size}x{grid_size}")
    
    # probar modelo
    print("="*60)
    print("prueba del modelo")
    print("="*60)
    
    obs, _ = env.reset()
    done = False
    total_reward = 0
    
    print(f"inicio: nodo {env.current_node}")
    print(f"objetivo: {waypoints} -> {destination}\n")
    
    # ejecutar episodio
    for step in range(500):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        
        total_reward += reward
        
        if step < 10 or done or truncated:
            print(f"  paso {step+1}: nodo {env.current_node}, reward={reward:.0f}")
        
        if done or truncated:
            break
    
    # obtener camino del info
    path = info.get("path", [])
    
    # mostrar resultados
    print("\n" + "="*60)
    if done:
        print(f"exito en {len(path)} pasos")
    elif truncated:
        print(f"truncado despues de {len(path)} pasos")
    else:
        print("fallo")
    
    print(f"recompensa: {total_reward:.0f}")
    print(f"camino: {path}")
    print("="*60)


if __name__ == "__main__":
    main()
