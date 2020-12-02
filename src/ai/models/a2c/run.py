import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import code

from src.ai.MeleeEnv import MeleeEnv
from src.ai.models.a2c.a2c import PPO, Memory

if __name__ == '__main__':
    env = MeleeEnv(fast_forward=True, blocking_input=True)
    
    episodes = 3000
    discount_factor = .5
    learning_rate = 0.001
    entropy_coeff = 0.2  # prefer exploration
    K_epochs = 4
    eps_clip = 0.2
    update_timestep = 120  # 2 seconds @60fps
    frame_skip = 1

    gpu = torch.device('cuda:0')
    cpu = torch.device('cpu')

    memory = Memory()
    ppo = PPO(env.observation_space.size, 
              env.action_space.size, 
              128, 
              learning_rate,
              discount_factor,
              entropy_coeff,
              K_epochs,
              eps_clip)

    # logging
    running_reward = 0
    avg_length = 0
    curr_episode = 0

    env.start()
    timestep = 0

    print("Training")
    for episode in range(curr_episode, episodes):
        print(f"Episode: {episode}")
        state, reward, done, info = env.setup()
        start_time = time.time()
        while not done:
            timestep += 1
            if timestep % frame_skip + 1 == 1:
                # only perform an action every 2 frames
                action = ppo.policy_old.act(state, memory)

            state, reward, done, info = env.step(action)

            if timestep % frame_skip + 1 == 1:
                # only record actions when we perform them
                memory.rewards.append(reward)
                memory.is_terminals.append(done)

            if timestep % update_timestep == 0:
                ppo.update(memory)
                memory.clear_memory()
                timestep = 0

            running_reward += reward
        end_time = time.time()
        print(f"Episode lasted {end_time - start_time}")

    env.close()

    # plt.title(f"Learning Rate")
    # plt.xlabel("Episode")
    # plt.ylabel("Reward")
    # plt.plot(train_rewards, label='train')
    # plt.plot(test_rewards, label='test')
    # plt.legend()
    # plt.show()
    print("Complete")
    sys.exit(0)

