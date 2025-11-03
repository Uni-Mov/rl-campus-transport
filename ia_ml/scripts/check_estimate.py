
from ia_ml.utils.estimate_training_time import estimate

num_episodes = 1000
steps_per_episode = 500

time_estimate = estimate(num_episodes, steps_per_episode)
print(f"Tiempo estimado de entrenamiento: {time_estimate:.2f} minutos") 
