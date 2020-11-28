import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import code

from src.ai.MeleeEnv import MeleeEnv
from src.ai.models.a2c.a2c import A2C, MLP
from src.ai.models.a2c.training import train, test

if __name__ == '__main__':
    episodes = 20
    discount_factor = .1
    learning_rate = 0.001

    gpu = torch.device('cuda:0')
    cpu = torch.device('cpu')

    env = MeleeEnv(fast_forward=False, blocking_input=False)
    env.init()

    policy = A2C(
        MLP((env.observation_space.size, 128, 128, env.action_space.size)),
        MLP((env.observation_space.size, 128, 128, 1))).to(device=cpu)

    optimizer = optim.Adam(policy.parameters(), lr=learning_rate)

    train_rewards = []
    test_rewards = []

    for episode in range(episodes):
        print("Training")
        p_loss, v_loss, train_reward = train(env, policy, optimizer, discount_factor, cpu)
        print("Testing")
        test_reward = test(env, policy, cpu)
 
    env.close()

    plt.title(f"Learning Rate")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.plot(train_rewards, label='train')
    plt.plot(test_rewards, label='test')
    plt.legend()
    plt.show()
    print("Complete")
    sys.exit(0)

