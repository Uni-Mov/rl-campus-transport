## Envs documentation

## WaypointNavigationEnv
This environment is a kickstart for experiments of **Reinformcement Learning with graphs**

## Description
The putpose of this environment is to simulate a graph navigation problem using **waypoints** and a **fixed destiny** over an osmnx graph

The main idea of this is follow a Markov Decission Process(MDP) following the next actions states and rewards.
State: an initial node + all the possible waypoints + the final destination
Action: Choose a neighbor
Reward: Penalty for bad steps, reward for reaching waypoints or destination


[Gymnasium Evironments Documentation](https://gymnasium.farama.org/api/env)