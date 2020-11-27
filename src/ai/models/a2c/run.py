import sys

import torch
import torch.nn as nn
import torch.optim as optim
from torch.multiprocessing import Process, Queue, Lock

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import code

from src.ai.MeleeEnv import MeleeEnv
from src.ai.models.a2c.a2c import A2C, MLP
from src.ai.models.a2c.training import train, test


if __name__ == '__main__':
    episodes = 10
    discount_factor = .99
    learning_rate = 0.001

    env = MeleeEnv(True)

    gpu = torch.device('cuda:0')
    torch.multiprocessing.set_start_method('fork')
    policy = A2C(
        MLP((env.observation_space.size, 128, 128, env.action_space.size)),
        MLP((env.observation_space.size, 128, 128, 1))).to(device=gpu)

    # init weights?

    optimizer = optim.Adam(policy.parameters(), lr=learning_rate)

    train_rewards = []
    test_rewards = []
    
    for episode in range(episodes):
        print(f"Episode: {episode}: training")
        policy_loss, value_loss, train_reward = train(env,
                                                      policy,
                                                      optimizer,
                                                      discount_factor,
                                                      device=gpu)
        
        print(f"Policy Loss: {policy_loss}\ Value Loss: {value_loss}")
        print(f"Train reward: {train_reward}")
        print(f"Episode: {episode}: testing")
        test_reward = test(env, policy, device=gpu)
        print(f"Test reward : {test_reward}")
        train_rewards.append(train_reward)
        test_rewards.append(test_reward)

    print("training complete") 
    plt.title(f"Learning Rate")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.plot(train_rewards, label='train')
    plt.plot(test_rewards, label='test')
    plt.legend()
    plt.show()
    print("Complete")
    sys.exit(0)

