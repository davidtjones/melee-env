from src.config.project import Project
import melee

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as distributions

import matplotlib.pyplot as plt
import numpy as np

from src.ai.tools import ActionSpace
from src.ai.training import train, evaluate
from src.ai.models.a2c import A2C, MLP
import code

p = Project()
p.set_ff(False)

console = melee.Console(
    path=str(p.slippi_bin),
    blocking_input=True)

controllers = {
    'ai': melee.Controller(console=console, port=1),
    'cpu': melee.Controller(console=console, port=2)}

console.run(iso_path=p.iso)
console.connect()

[v.connect() for k,v in controllers.items()]

env = {
    "console": console,
    "controllers": controllers,
    "ACT": ActionSpace(),
    "OBS": None
}

discount_factor = .99
learning_rate = 0.001
total_episodes = 3000

gpu = torch.device('cuda:0')
cpu = torch.device('cpu')
device = gpu

policy = A2C(MLP((env["OBS"].size, 128, 128, env["ACT"].size)),
             MLP((env["OBS"].size, 128, 128, 1)).to(device=device))

# layer initialization

optimizer = optim.Adam(policy.parameters(), lr=learning_rate)

train_rewards = []
test_rewards = []

while total_episodes != 0:
    gamestate = console.step()
    
    if gamestate.menu_state is melee.Menu.CHARACTER_SEELCT:
        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controllers['ai'],
                                          costume=3,
                                          swag=False,
                                          start=True)

        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controllers['cpu'],
                                          cpu_level=1,
                                          swag=False,
                                          start=False)

    elif gamestate.menu_state is melee.Menu.STAGE_SELECT:
        melee.MenuHelper.choose_stage(stage=melee.enums.Stage.FINAL_DESTINATION,
                                      gamestate=gamestate,
                                      controller=controllers['ai'])

    elif gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        # perform training here
        for phase in ['train', 'test']:
            if phase == 'train':
                policy_loss, value_loss, train_reward = train(env,
                                                              policy,
                                                              optimizer,
                                                              discount_factor,
                                                              device=device)
            if phase == 'test':
                test_reward = evaluate(console,
                                       controllers,
                                       policy,
                                       device=device)

    train_rewards.append(train_reward)
    test_rewards.append(test_reward)

# plotting

