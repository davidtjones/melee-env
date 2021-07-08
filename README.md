melee-env
---
melee-env wraps the fantastic [libmelee](https://github.com/altf4/libmelee) as a more gym-esque environment with less boilerplate and setup. Additionally, melee-env provides a convenient and highly flexible framework for creating your own agents. For more information on these topics and melee-env, see the [README](melee_env/agents/README.md) in the agents folder.

### Code example: 
```python
from melee import enums
from melee_env.env import MeleeEnv
from melee_env.agents.basic import *
import argparse

players = [Rest(), NOOP(enums.Character.FOX)]

env = MeleeEnv('path/to/iso', players, fast_forward=True)

episodes = 10; reward = 0
env.start()

for episode in range(episodes):
    gamestate, done = env.setup(enums.Stage.BATTLEFIELD)
    while not done:
        for i in range(len(players)):
            players[i].act(gamestate)
        gamestate, done = env.step()
```

### Video Demonstration
[![IClick me!](https://img.youtube.com/vi/c-MyFS2PAu8/0.jpg)](https://www.youtube.com/watch?v=c-MyFS2PAu8)

This library has been designed with flexibility in mind. The action space, observation space, and the agents are completely modular, and there are only a few requirements to build your own. 

## Note
This library requires Slippi, which in turn requires an SSBM 1.02 NTSC/PAL ISO. This library does not and will not distribute this. You must acquire this on your own!

## Installation
Install from pip: `pip install melee-env`. Test by running `agents_example.py --iso=/path/to/your/iso` 

## Platform support
* Linux
* Windows