import sys

import torch
import torch.nn as nn
import torch.optim as optim
from torch.multiprocessing import Process, Queue, Lock
from multiprocessing.managers import BaseManager

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import code

from src.ai.MeleeEnv import MeleeEnv
from src.ai.models.a2c.a2c import A2C, MLP
from src.ai.models.a2c.async_training import train, test, update

class TrainProxy(Process):
    def __init__(self, q, network, optimizer):
        Process.__init__(self)
        self.q = q
        self.network = network
        self.optimizer = optimizer

    def run(self):
        self.listen()
        print("trainer started")

    def listen(self):
        print("waiting for data")
        while True:
            data = self.q.get()
            print(data)


if __name__ == '__main__':
    episodes = 2
    discount_factor = .25
    learning_rate = 0.001

    gpu = torch.device('cuda:0')
    cpu = torch.device('cpu')

    torch.multiprocessing.set_start_method('fork')
    
    env = MeleeEnv(fast_forward=True, blocking_input=False)
    policy = A2C(
        MLP((env.observation_space.size, 128, 128, env.action_space.size)),
        MLP((env.observation_space.size, 128, 128, 1))).to(device=cpu)

    policy.share_memory()

    optimizer = optim.Adam(policy.parameters(), lr=learning_rate)

    q = Queue() 
    trainer = TrainProxy(q, policy, optimizer)
    trainer.start()
    
    train_rewards = []
    test_rewards = []

    env.start()

    for episode in range(episodes):
        actions, rewards, values = train(env, policy, cpu)
        train_reward = sum(rewards)
        q.put({"train": [actions, rewards, values]})
        test_reward = test(env, policy, cpu)
        
 
    env.close()
    print("training complete") 

    # plt.title(f"Learning Rate")
    # plt.xlabel("Episode")
    # plt.ylabel("Reward")
    # plt.plot(train_rewards, label='train')
    # plt.plot(test_rewards, label='test')
    # plt.legend()
    # plt.show()
    print("Complete")
    sys.exit(0)

