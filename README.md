melee-env
---
This repo contains an implemention of Melee as a Gym-esque environment.

### Code example: 
```python
from melee import enums
from melee_env.env import MeleeEnv
from melee_env.agents.util import ActionSpace, ObservationSpace
from melee_env.agents.basic import *

players = [Rest(), Shine(), Random(enums.Character.FALCO), CPU(enums.Character.LINK, 3)]

env = MeleeEnv(
    "path/to/iso",
    players,
    ActionSpace(),
    ObservationSpace(),
    ai_starts_game=True,
    fast_forward=False, 
    blocking_input=True)

env.start()
episodes = 10; reward = 0; done = False

for episode in range(episodes):
    observation, reward, done, info = env.setup(enums.Stage.BATTLEFIELD)
    while not done:
        for i in range(len(players)):
            if players[i].agent_type == "AI":  # only process AI players
                players[i].act(observation, env.action_space)

        observation, reward, done, info = env.step()        
```

### Video Demonstration
[![IClick me!](https://img.youtube.com/vi/c-MyFS2PAu8/0.jpg)](https://www.youtube.com/watch?v=c-MyFS2PAu8)

This library has been designed with flexibility in mind. The action space, observation space, and the agents are completely modular, and there are only a few requirements to build your own. For more information on these topics, see the [README](melee_env/agents/README.md) in the agents folder. 

## Note
This library requires Slippi, which in turn requires an SSBM 1.02 NTSC/PAL ISO. This library does not and will not distribute this. You must acquire this on your own!

## Installation
Install from pip: `pip install melee-env`. Test by running `agents_example.py --iso=/path/to/your/iso` 

## Platform support
* Linux
* Windows

## Some notes:
* This library is specifically intended for the development of AI using reinforcement learning (or possibly computer vision). This library abstracts away much of the functionality of libmelee so that developers/researchers can focus on AI. I am not sure how difficult it would be implement something that used more traditional strategies, but it may be easier to work directly with libmelee in that case.
* There are currently no plans to support stages outside of the tournament-legal stages.