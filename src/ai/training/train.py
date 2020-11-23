import numpy as np
import melee
import code

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributional as F

import matplotlib.pyplot as plt

def train(policy, optimizer, discount_factor, normalize=True, device=torch.device("cpu")):

    policy.train()
    optimizer.zero_grad()
    critic_criterion = nn.SmoothL1Loss()

    log_prob_actions = []
    values = []
    rewards = []

    # play a game
    while not done:

