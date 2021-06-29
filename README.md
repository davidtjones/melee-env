actor-critic bot
---

## About
This repo contains an implemention of Melee as a Gym-esque environment. It also includes an actor critic agent implemented on this environment. 

### Code sample: 
```python
from src.ai.MeleeEnv import MeleeEnv
import matplotlib.pyplot as plt

# make the environment
env = MeleeEnv(fast_forward=False, blocking_input=False) 

episodes = 10 

env.start()
for episode in range(episodes):
    # get to versus mode and select characters, start match
    observation, reward, done, info = env.setup()

    # input actions until the match is finished
    while not done:
        print(observation.flatten())
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)

```

## Note
This library requires Slippi, which in turn requires an SSBM 1.02 NTSC/PAL ISO. This library does not and will not distribute this. You must acquire this on your own!

## Setup
You must have your own copy of Super Smash Bros Melee as well as the Slippi Online AppImage (get started here: https://slippi.gg). Move the AppImage into `src/Slippi`. Additional setup has been mostly automated: 
1. `cd ac-bot`
2. Conda recommended. Install from `environment.yml`. Complete environment installation by adding `src` to the environment with `pip install -e .`
3. cd `src`
4. Run `python setup/genconfig.py`. Optionally pass in your (legally obtained) ISO via `--iso=path/to/iso` to load the ISO on startup (highly recommended). 
5. (Optional) Test your installation. Run `python tests/shine.py`. Be sure to press enter when prompted. 


Some notes:
* If you notice that controllers aren't working, check the config in dolphin and verify that the controller profile is setup correctly. The automation steps should take care of this. You can verify the controller config for the bot is correct by checking Controllers -> [port X] -> Configure and verifying that the resulting window looks like [this](https://user-images.githubusercontent.com/609563/86555862-7dd45d80-bf06-11ea-8d7e-e4d8007f66a3.png). You should be able to load the slippibot profile to fix this.


