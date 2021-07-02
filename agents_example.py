from melee_env.env import MeleeEnv
from ..tests.util.observation_space import ObservationSpace
from ..tests.util.action_space import ActionSpace
from melee_env.agents.basic import *

# Setup the Agents, Melee supports 2-4 players
players = [Human(), Shine()]  #, Random(), CPU(8)]

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
