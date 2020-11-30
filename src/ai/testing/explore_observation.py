from src.ai.MeleeEnv import MeleeEnv
import matplotlib.pyplot as plt

# make the environment
env = MeleeEnv(p2_human=True) 

episodes = 1

env.start()
for episode in range(episodes):
    # get to versus mode and select characters, start match
    observation, reward, done, info = env.setup()
    total_reward = 0 

    # input actions until the match is finished
    while not done:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        print(f"Facing: {obs[4][1]} | X: {obs[5][1]} | Y: {obs[6][1]} | action: {obs[7][1]} | action_frame: {obs[8][1]}")



