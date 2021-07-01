from src.ai.MeleeEnv import MeleeEnv
from src.ai.util.observation_space import ObservationSpace
from src.ai.util.action_space import ActionSpace
from src.ai.agents.basic import *
import numpy as np

# Setup the Agents
players = [Human(), Shine(), Random(), CPU(8)]

# make the environment
env = MeleeEnv(
    players,
    ActionSpace(),
    ObservationSpace(),
    fast_forward=False, 
    blocking_input=True)

episode_count = 100
reward = 0
done = False

env.start(); observation, reward, done, info = env.setup()

while not done:
    print(observation)
    for i in range(len(players)):
        if players[i].agent_type == "AI":
            players[i].act(observation[i], env.action_space)

    observation, reward, done, info = env.step()
