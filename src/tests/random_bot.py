from src.ai.MeleeEnv import MeleeEnv
from src.ai.util.observation_space import ObservationSpace
from src.ai.util.action_space import ActionSpace
from src.ai.agents.basic import *
import numpy as np
import code

# Setup the Agents
players = [Human(), Shine()]

# make the environment
env = MeleeEnv(
    players,
    ActionSpace(),
    ObservationSpace(),
    fast_forward=False, 
    blocking_input=True)


episodes = 2

env.start()
for episode in range(episodes):
    # get to versus mode and select characters, start match
    observation, reward, done, info = env.setup()
    # input actions until the match is finished
    while not done:
        
        print(observation)
        for i in range(len(players)):
            if players[i].defeated == True and len(observation) < len(players):
                # insert the missing row
                observation = np.insert(observation, i, [-1, -1, -1, 0], axis=0)

            if players[i].agent_type == "AI" and players[i].defeated == False:
                players[i].act(observation[i], env.action_space)

        observation, reward, done, info = env.step()
        print("---")
