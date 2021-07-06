from melee import enums
from melee_env.env import MeleeEnv
from melee_env.agents.util import ActionSpace, ObservationSpace
from melee_env.agents.basic import *
import argparse

parser = argparse.ArgumentParser(description="Example melee-env demonstration.")
parser.add_argument("--iso", default=None, type=str, 
    help="Path to your NTSC 1.02/PAL SSBM Melee ISO")

args = parser.parse_args()

players = [Rest(), Shine(), Random(enums.Character.FALCO), CPU(enums.Character.LINK, 3)]

env = MeleeEnv(
    args.iso,
    players,
    ActionSpace(),
    ObservationSpace(),
    ai_starts_game=True,
    fast_forward=False, 
    blocking_input=True)

env.start()
episodes = 10; reward = 0; done = False

for episode in range(episodes):
    observation, reward, done, info = env.setup(enums.Stage.BATTLEFIELD)
    while not done:
        for i in range(len(players)):
            if players[i].agent_type == "AI":  # only process AI players
                players[i].act(observation, env.action_space)

        observation, reward, done, info = env.step()
