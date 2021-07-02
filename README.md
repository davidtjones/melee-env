melee-env
---

This repo contains an implemention of Melee as a Gym-esque environment. 

### Code example: 
```python
from melee_env.env import MeleeEnv
from melee_env.agents.util import ObservationSpace, ActionSpace
from melee_env.agents.basic import *

# Setup the Agents, Melee supports 2-4 players
players = [Human(), Shine(), Random(enums.Character.FALCO), CPU(enums.Character.LINK, 3)]

# make the environment
env = MeleeEnv(
    "path/to/iso",
    players,
    ActionSpace(),
    ObservationSpace(),
    fast_forward=False, 
    blocking_input=True)

episodes = 10; reward = 0; done = False
env.start()

for episode in range(episodes):
    observation, reward, done, info = env.setup(enums.Stage.BATTLEFIELD)
    while not done:
        print(observation)
        for i in range(len(players)):
            if players[i].agent_type == "AI":  # only process AI players
                players[i].act(observation[i], env.action_space)

        observation, reward, done, info = env.step()
        
```
This library has been designed with flexibility in mind. The action and observation spaces are completely modular, and custom spaces are supported. 

## Note
This library requires Slippi, which in turn requires an SSBM 1.02 NTSC/PAL ISO. This library does not and will not distribute this. You must acquire this on your own!

## Installation
Install from pip: `pip install melee-env`. Test by running the above example. 

## Platform support
* Linux
* Windows (planned)

## Some notes:
* If you notice that controllers aren't working, check the config in dolphin and verify that the controller profile is setup correctly. The automation steps should take care of this. You can verify the controller config for the bot is correct by checking Controllers -> [port X] -> Configure and verifying that the resulting window looks like [this](https://user-images.githubusercontent.com/609563/86555862-7dd45d80-bf06-11ea-8d7e-e4d8007f66a3.png). You should be able to load the slippibot profile to fix this. Unsure if this is still an issue.


