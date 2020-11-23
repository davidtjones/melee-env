import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self, input_size):

        self.net = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.Dropout(p=0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.Dropout(p=0.5),
            nn.Linear(64, 32),
            nn.Linear(32, 1))
        

    def forward(self, x):
        return self.net(x)
        

