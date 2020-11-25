from src.ai.env import MeleeEnv

# make the environment
env = MeleeEnv() 
action_space_size = env.action_space.size

# initialize the game itself
observation, reward, done, info = env.setup()

while not done:
    action = env.action_space.sample()
    observation, reward, done, info = env.step(action)
    print(f"{observation}, {reward}, {done}, {info}")
print("Complete")



