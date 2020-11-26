from src.ai.MeleeEnv import MeleeEnv
import matplotlib.pyplot as plt

# make the environment
env = MeleeEnv(True) 

episodes = 10 
agent_reward = []
for episode in range(episodes):
    # get to versus mode and select characters, start match
    observation, reward, done, info = env.setup()
    total_reward = 0 

    # input actions until the match is finished
    while not done:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        total_reward += reward

    agent_reward.append(total_reward)

print("Complete")
print(agent_reward)
plt.plot(agent_reward)
plt.title("Agent Reward")
plt.ylabel("Reward")
plt.xlabel("Episode")
plt.show()



