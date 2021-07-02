from melee_env.env import MeleeEnv
from melee_env.agents.util import ObservationSpace, ActionSpace
from melee_env.agents.basic import *

# Setup the Agents, Melee supports 2-4 players
players = [Human(), Shine(), Random(), CPU(3)]

# make the environment
env = MeleeEnv(
    "path/to/iso",
    players,
    ActionSpace(),
    ObservationSpace(),
    fast_forward=False, 
    blocking_input=True)

episodes = 10; reward = 0; done = False

env.start()
observation, reward, done, info = env.setup()

for episode in range(episodes):
    while not done:
        print(observation)
        for i in range(len(players)):
            if players[i].agent_type == "AI":  # only process AI players
                players[i].act(observation[i], env.action_space)

        observation, reward, done, info = env.step()
