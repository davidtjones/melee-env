actor-critic bot
---

## Setup
You must have your own copy of Super Smash Bros Melee as well as the Slippi Online AppImage (get started here: https://slippi.gg). Move the AppImage into `src/Slippi`. Additional setup has been mostly automated: 

1. Install the environment using miniconda (placeholder)
2. Navigate the `src` directory
3. Run `python config/genconfig.py`. Optionally pass in your ISO via `--iso=path/to/iso to load the game more quickly.`
4. Run `python Slippi/tools/unpack.py` to extract the game from the appimage. This will also form a portable installation. The appimage can be safely deleted at this point.
5. Run `python Slippi/tools/apply_gecko_codes.py` to apply the custom gecko codes needed to run libmelee
6. Finally, run `python Slippi/tools/configure` to link your portable installation to the extracted game as well as to set Slippi configuration options. 
7. (Optional) Test your installation. Run `python tests/shine.py`. Be sure to press enter when prompted. 


Some notes:
* When executing actions on a given frame, you are looking for the falling edge of the previous frame
	* Fox multishine for example:
		* Shine on frame 1
		* Jump on frame 1 of jump squat => after frame 3 of kneebend
* ~~If you notice that controllers aren't working, check the config in dolphin and verify that the controller profile is setup correctly. I have placed a working GCPadNew.ini in this repo.~~ This should be fixed by the new automation steps!


The [SLP Dataset](https://drive.google.com/file/d/1ab6ovA46tfiPZ2Y3a_yS1J3k3656yQ8f/view?usp=sharing) is tentatively required for the initial training setup. It needs to be placed in or linked to src/training/dataset/slp

