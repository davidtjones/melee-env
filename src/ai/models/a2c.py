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

class ActorNetwork(nn.Module):
    def __init__(self, input_layer_size, output_layer_size, main_stick_size):
        """
        This network takes in the current gamestate and outputs the 'best' 
          next action. For simple gym apps this is simple since these just
          amount of n-state buttons. CartPole is left, right, noop. LunarLander
          is left, right, main, or nothing. Notice that firing main AND left is
          not an option. Melee has numerous states that require an AND. So it 
          is therefore necessary to regress action on each button individually. 
            
          There are
          - 5 regular buttons with 2 states each.
          - 2 triggers with 3 states each.
          - 1 c-stick that is 5 states
          - 1 main stick with `main_stick_size` states

          This network will embed the gamestate into some higher dimension,
          then expand back up to the predicted action, which will be 
          5*2 + 2*3 + 5 + `main_stick_size` = 21 + `main_stick_size`

        """
        
        self.input_layer = nn.Linear(input_layer_size, 512)
        self.hidden_layer1 = nn.Linear(512, 256)
        self.hidden_layer2 = nn.Linear(256, 128)
        self.hidden_layer3 = nn.Linear(128, 64)
        self.hidden_output = nn.Linear(64, 21+main_stick_size)

        
class A2C(nn.Module):
    def __init__(self, actor, critic):
        super().__init__()

        self.actor = actor
        self.critic = critic

    def forward(self, state):
        action = self.actor(state)
        value = self.critic(state)

        return action, value




            

