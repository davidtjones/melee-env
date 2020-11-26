from src.ai.MeleeEnv import MeleeEnv

# make the environment
env = MeleeEnv() 

episodes = 2

for episode in range(episodes):
    # get to versus mode and select characters, start match
    observation, reward, done, info = env.setup()
    
    # input actions until the match is finished
    while not done:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        print(f"{episode} {obs}, {reward}, {done}, {info}")

print("Complete")



