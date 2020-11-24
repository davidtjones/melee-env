import train
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as distributions

import matplotlib.pylot as plt
import numpy as np
import melee

def train(env, policy, optimizer, discount_factor, device):
    policy.train()
    optimizer.zero_grad()
    critic_criterion = nn.SmoothL1Loss()

    # reset to new game
    while gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        # perform actions
        gamestate = console.step()

        # preds = policy(gamestate)
        # action_prob = F.softmax(preds[0], dim=-1)
        # m = distributions.Categorical(action_prob)
        # action = m.sample()
        # log_prob_action = m.log_prob(action)
        #
        # state, reward, done, info = env.step(action.item())

        # log_prob_actions.append(log_prob_action)
        # values.append(preds[1])
        # rewards.append(reward)


    # we are no longer in a game but still in training
    # log_prob_actions = torch.cat(log_prob_actions).to(device=device)
    # values = torch.cat(values).squeeze(-1).to(device=device)

    # returns = []
    # R = 0

    # for r in rewards[::-1]:
    #     R = r + R * discount_factor
    #     returns.append(R)

    # returns = torch.tensor(returns[::-1]).to(device=device)
    # returns = (returns - returns.mean())/returns.std()

    # advantages = returns - values
    # advantages = (advantages - advantages.mean())/advantages.std()

    # policy_loss = -(advantages.detach() * log_prob_actions).sum()
    # value_loss = critic_criterion(returns.detach().float(), values.float()).sum()

    # Update
    # policy_loss.backward()
    # value_loss.backward()
    optimizer.step()

    return policy_loss, value_loss, sum(rewards)

    

    

