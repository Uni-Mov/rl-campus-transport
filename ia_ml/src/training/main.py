"""
script de entrenamiento para navegacion con waypoints usando ppo.
"""
import networkx as nx
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
from ia_ml.src.envs.waypoint_navigation import WaypointNavigationEnv


def main():
    # crear grafo 
    grid_size = 10
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
    env = WaypointNavigationEnv(G, waypoints, destination, max_steps=80)
    
    # configurar modelo ppo
    # mlppolicy: red neuronal multicapa que recibe estado y devuelve accion
    model = PPO(
        "MlpPolicy", 
        env, 
        learning_rate=3e-4,      # que tan rapido aprende (0.0003)
        clip_range=0.2,          # que tan drasticos son los cambios (limita actualizaciones)
        ent_coef=0.05,       # cuanta exploracion hace (balance exploration/exploitation)
        gamma=0.99,              # cuanto valora el futuro (descuento recompensas futuras)
        gae_lambda=0.95,         # como calcula si una accion fue buena (advantage estimation)
        verbose=1
    )
    
    # crear entorno de evaluacion
    eval_env = WaypointNavigationEnv(G, waypoints, destination, max_steps=30)
    
    # callback para detener si no mejora
    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=10,  # detener si no mejora en 10 evaluaciones
        min_evals=5,                  # minimo 5 evaluaciones antes de poder parar
        verbose=1
    )
    
    # callback de evaluacion (cada 5k steps)
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=f"./logs/best_model_{grid_size}x{grid_size}/",
        log_path=f"./logs/results_{grid_size}x{grid_size}/",
        eval_freq=5_000,              # evaluar cada 5k steps
        n_eval_episodes=5,            # 5 episodios por evaluacion
        deterministic=True,
        callback_after_eval=stop_callback,
        verbose=1
    )
    
    # entrenar
    model.learn(total_timesteps=200_000, callback=eval_callback)
    
    # cargar mejor modelo encontrado
    print("\n" + "="*60)
    print("cargando mejor modelo")
    print("="*60)
    best_model_path = f"./logs/best_model_{grid_size}x{grid_size}/best_model"
    model = PPO.load(best_model_path, env=env)
    
    # guardar modelo final
    model.save(f"ppo_waypoint_{grid_size}x{grid_size}")
    
    # probar modelo
    print("\n" + "="*60)
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
