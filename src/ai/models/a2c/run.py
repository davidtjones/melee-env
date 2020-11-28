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
from src.ai.models.a2c.a2c import A2C, MLP
from src.ai.models.a2c.training import train, test

if __name__ == '__main__':
    episodes = 3000
    discount_factor = .1
    learning_rate = 0.001

    gpu = torch.device('cuda:0')
    cpu = torch.device('cpu')

    env = MeleeEnv(fast_forward=False, blocking_input=False)

    policy = A2C(
        MLP((env.observation_space.size, 128, 128, env.action_space.size)),
        MLP((env.observation_space.size, 128, 128, 1))).to(device=cpu)

    optimizer = optim.Adam(policy.parameters(), lr=learning_rate)

    train_rewards = []
    test_rewards = []
    best_reward = -100000
    curr_episode = 0

    if Path("policy.pt").exists():
        path = Path("policy.pt")
        checkpoint = torch.load(path)
        curr_episode = checkpoint['episode']
        policy.load_state_dict(checkpoint['policy_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        best_reward = checkpoint['best_reward']
        train_rewards = checkpoint['train_rewards']
        test_rewards = checkpoint['test_rewards']
        learning_rate = checkpoint['learning_rate']
        discount_factor = checkpoint['discount_factor']
        print("Loaded Previous Run!")

    env.init()
    


    for episode in range(curr_episode, episodes):
        start_time = time.time()
        print(f"Episode: {episode}")
        print("Training")
        p_loss, v_loss, train_reward = train(env, policy, optimizer, discount_factor, cpu)
        print("Testing")
        test_reward = test(env, policy, cpu)
        if test_reward > best_reward:
            print("Model Saved")
            torch.save(
                {
                    'episode': episode,
                    'policy_state_dict': policy.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'best_reward': best_reward,
                    'discount_factor': discount_factor,
                    'learning_rate': 0.001,
                    'train_rewards': train_rewards,
                    'test_rewards': test_rewards
                }, "policy.pt")
        end_time = time.time()
        print(f"Episode lasted {end_time - start_time}")

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

