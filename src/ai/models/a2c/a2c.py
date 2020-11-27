import torch
import torch.nn as nn


# Networks
class MLP(nn.Module):
    def __init__(self, layer_sizes, dropout=0.1):
        super().__init__()

        layers = []

        for i in range(len(layer_sizes)-2):
            layers.append(nn.Linear(layer_sizes[i], layer_sizes[i+1]))
            layers.append(nn.Dropout(dropout))
            layers.append(nn.ReLU())

        layers.append(nn.Linear(layer_sizes[-2], layer_sizes[-1]))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class A2C(nn.Module):
    def __init__(self, actor, critic):
        super().__init__()

        self.actor = actor
        self.critic = critic

    def forward(self, state):
        action = self.actor(state)
        value = self.critic(state)

        return action, value




            

