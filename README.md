melee-env
---

This repo contains an implemention of Melee as a Gym-esque environment. 

### Code sample: 
```python
from melee_env.env import MeleeEnv
from melee_env.agents.util import ObservationSpace, ActionSpace
from melee.agents.basic import *

# Setup the Agents, Melee supports 2-4 players
players = [Human(), Shine(), Random(), CPU(8)]

# make the environment
env = MeleeEnv(
    players,
    ActionSpace(),
    ObservationSpace(),
    fast_forward=False, 
    blocking_input=True)

episode_count = 100
reward = 0
done = False

env.start(); observation, reward, done, info = env.setup()

while not done:
    print(observation)
    for i in range(len(players)):
        if players[i].agent_type == "AI":
            players[i].act(observation[i], env.action_space)

    observation, reward, done, info = env.step()

```
This library has been designed with flexibility in mind. The action and observation spaces are completely modular, and custom spaces are supported. 

## Note
This library requires Slippi, which in turn requires an SSBM 1.02 NTSC/PAL ISO. This library does not and will not distribute this. You must acquire this on your own!

## Setup
1. `cd ac-bot`
2. Conda recommended. Install from `environment.yml`. Complete environment installation by adding `src` to the environment with `pip install -e .`
3. cd `src`
4. Run `python setup/genconfig.py`. Optionally pass in your (legally obtained) ISO via `--iso=path/to/iso` to load the ISO on startup (highly recommended). 
5. (Optional) Test your installation. Run `python tests/shine.py`. You can run `python tests/agent_test.py` if you have a gamecube controller and a gamecube controller USB adapter, or change the `Human` agent on line 8 to some other agent.

## Platform support
* Linux
* Windows (planned)

Some notes:
* If you notice that controllers aren't working, check the config in dolphin and verify that the controller profile is setup correctly. The automation steps should take care of this. You can verify the controller config for the bot is correct by checking Controllers -> [port X] -> Configure and verifying that the resulting window looks like [this](https://user-images.githubusercontent.com/609563/86555862-7dd45d80-bf06-11ea-8d7e-e4d8007f66a3.png). You should be able to load the slippibot profile to fix this. Working on a fix for this.


