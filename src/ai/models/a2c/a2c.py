import torch
import torch.nn as nn
from torch.distributions import Categorical
import code
# Networks

class Debug(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        print(x)
        print(x.shape)
        return x

class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]

class ActorCritic(nn.Module):
    def __init__(self, 
                 obs_space_size, 
                 action_space_size, 
                 hidden_size):
        # input_size: number of input features
        # output_size: action space size for actor
        super().__init__()

        # actions go through this embedding first
        self.action_embedding = nn.Embedding(400, 200)
        
        self.actor = nn.Sequential(
            nn.Linear(200+obs_space_size-2, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_space_size),
            nn.Softmax(dim=-1)
        )

        self.critic = nn.Sequential(
            nn.Linear(200+obs_space_size-2, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )

    def build_feature_vector(self, state):
        # x: input with shape [1, obs_space_size]
        # actions go through embedding
        
        actions = state[:, 14:16].long()
        interaction = self.action_embedding(actions[:, 0]) - self.action_embedding(actions[:, 1])
        action_frames = state[:, 16:18]
        continuous_features = state[:, 0:14]
        features = torch.cat([continuous_features,
                              interaction,
                              action_frames], dim=1)

        return features

    def act(self, state, memory):
        
        state = torch.tensor(
            state.flatten().reshape(1, -1),
            dtype=torch.float32)

        action_probs = self.actor(self.build_feature_vector(state))
        dist = Categorical(action_probs)
        action = dist.sample()

        memory.states.append(state)
        memory.actions.append(action)
        memory.logprobs.append(dist.log_prob(action))

        return action.item()


    def evaluate(self, state, action): 
        features = self.build_feature_vector(state)
        action_probs = self.actor(features)
        dist = Categorical(action_probs)

        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()

        state_value = self.critic(features)

        return action_logprobs, torch.squeeze(state_value), dist_entropy


class PPO:
    def __init__(self, state_dim, action_dim, n_latent_var, lr, gamma, beta, K_epochs, eps_clip):
        self.lr = lr
        self.gamma = gamma
        self.beta = beta
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        self.policy = ActorCritic(state_dim, action_dim, n_latent_var)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr)
        self.policy_old = ActorCritic(state_dim, action_dim, n_latent_var)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.value_loss = nn.MSELoss()

    def update(self, memory):
        # monte carlo estimate of state rewards:
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(memory.rewards), reversed(memory.is_terminals)):
            if is_terminal:
                discounted_rewards = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)

        rewards = torch.tensor(rewards, dtype=torch.float32)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        old_states = torch.cat(memory.states, dim=0).detach()
        old_actions = torch.stack(memory.actions).detach()
        old_logprobs = torch.stack(memory.logprobs).detach()

        # optimize
        for _ in range(self.K_epochs):
            # evaluate old actions and values
            logprobs, state_values, dist_entropy = self.policy.evaluate(old_states, old_actions)

            # get ratio pi_theta/pi_theta_old
            ratios = torch.exp(logprobs - old_logprobs.detach())

            # Surrage loss
            advantages = rewards - state_values.detach()
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
            loss = -torch.min(surr1, surr2) + 0.5*self.value_loss(state_values, rewards) - 0.01*dist_entropy

            # take gradient step
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()

        # copy new weights into old policy
        self.policy_old.load_state_dict(self.policy.state_dict())

                                                                  





if __name__=="__main__":
    # test an input:
    input = torch.tensor([
        4, 0, 4, 0, 
        2, 2, 0, 0, 
        1, 0, 246, -246, 100, -100,
        200, 129, 3, 20])

    net_test = ActorCritic(input.shape[0], 45, 
                           [8, 9, 14, 15],
                           [(2, 1), (2, 1), (383, 200), (383, 200)],
                           [128, 128, 128])

    output = net_test(input)
    print(output)
            

