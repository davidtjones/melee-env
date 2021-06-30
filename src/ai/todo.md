# TO DO

## Working with libmelee
* create a better console object (a wrapper for libmelee?) that exposes more functionality to dolphin itself
* create pull request adding pathlib for proper path handling
* write new functionality to control what is connected to each port
	- [Core] contains items sidevice[0-3] which can take values
	- 0: None
	- 6: Standard Controller
	- 12: Gamecube Controller Adapter
	- seems useful for switching modes quickly (i.e., we want two bots in one scenario, but then another test script where a human player can interact with the environment)

## AI
A conversation with Dr. Harrison, in bullet points
* Get rid of stocks in the state (every time lose: new state)
* Maybe penalize for going off stage (seems not robust)
* don't teach complex things
* curriculum learning? <3
* self play (after beating level 1 bot)
	- I think the discussion was that this was only useful after things were working
* A3C (breaks correlation)
	- useful for after mainline integration
* batch sampling (PPO) (already integrated?)
* image feature / latent representation
* discrete X/Y grid to reduce obv space

