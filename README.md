actor-critic bot
---

## About
This bot runs actor-critic. One of the key elements of any reinforcement-learning agent is the reward signal received at each time step. 


## Setup
You must have your own copy of Super Smash Bros Melee as well as the Slippi Online AppImage (get started here: https://slippi.gg). Move the AppImage into `src/Slippi`. Additional setup has been mostly automated: 

1. Install the environment using miniconda / pip
2. Navigate the `src` directory
3. Run `python config/genconfig.py`. Optionally pass in your ISO via `--iso=path/to/iso to load the game more quickly.`
4. Run `python Slippi/tools/unpack.py` to extract the game from the appimage. This will also form a portable installation. The appimage can be safely deleted at this point.
5. Run `python Slippi/tools/apply_gecko_codes.py` to apply the custom gecko codes needed to run libmelee
6. Finally, run `python Slippi/tools/configure` to link your portable installation to the extracted game as well as to set Slippi configuration options. 
7. (Optional) Test your installation. Run `python tests/shine.py`. Be sure to press enter when prompted. 


Some notes:
* ~~If you notice that controllers aren't working, check the config in dolphin and verify that the controller profile is setup correctly. I have placed a working GCPadNew.ini in this repo.~~ This should be fixed by the new automation steps!


