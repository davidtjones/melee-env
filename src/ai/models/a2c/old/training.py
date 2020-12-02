import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributions as distributions
import torch.nn.functional as F

import signal

def train(env, policy, optimizer, discount_factor, device):
    # only one producer can produce examples at a time since there is only one
    #   instance of dolphin available. 
    env.setup()
    
    log_prob_actions = []
    rewards = []
    values = []
    entropies = []
    state, reward, done, info = env.setup()
    prev_info = None
    curr_time = time.time()

    while not done:

        state = torch.tensor(
            state.flatten(), 
            dtype=torch.float32
        ).unsqueeze(0).to(device=device)

        preds = policy(state)
        action_prob = F.softmax(preds[0], dim=-1)
        m = distributions.Categorical(action_prob)
        action = m.sample()
        entropy = m.entropy()

        state, reward, done, info = env.step(action.item())
            
        log_prob_actions.append(m.log_prob(action))
        rewards.append(reward)
        values.append(preds[1])
        entropies.append(entropy)

        if time.time() > curr_time + 2: # info is "dead" and prev_info is None:
            print(f"Total Reward: {sum(rewards)}...updating policy")     
            log_prob_actions = torch.cat(log_prob_actions).to(device=device)
            values = torch.cat(values).squeeze(-1).to(device=device)

            returns = []
            R = 0

            for r in rewards[::-1]:
                R = r + R * discount_factor
                returns.append(R)

            returns = torch.tensor(returns[::-1]).to(device=device)
            if returns.std() != 0:
                returns = (returns - returns.mean())/returns.std()

            advantages = returns - values
            if advantages.std() != 0:
                advantages = (advantages.mean())/advantages.std()

            critic_criterion = nn.SmoothL1Loss()
            optimizer.zero_grad()
            policy_loss = -(advantages.detach() * log_prob_actions).sum()
            value_loss  = critic_criterion(returns.detach().float(), values.float()).sum()
            entropy_loss = torch.cat(entropies).sum()
            print(f"Policy Loss: {policy_loss}, Value Loss: {value_loss}, B*Entropy Loss: {beta*entropy_loss}")


            # Update
            loss = policy_loss + value_loss - (beta * entropy_loss)
            loss.backward()
            optimizer.step()
        
            log_prob_actions = []
            rewards = []
            values = []
            entropies = []
            curr_time = time.time()


        prev_info = info

    return policy_loss, value_loss, sum(rewards)
    
    
def test(env, policy, device=None):
    env.setup() 
   
    policy.eval()
    total_reward = 0
    state, reward, done, info = env.setup()
    while not done:
        state = torch.tensor(
            state.flatten(), 
            dtype=torch.float32
        ).unsqueeze(0).to(device=device)

        with torch.no_grad():
            preds = policy(state)
            action_prob = F.softmax(preds[0], dim=-1)
        
        action = torch.argmax(action_prob, dim=-1)
        state, reward, done, info = env.step(action.item())
        total_reward += reward

    return total_reward
 
