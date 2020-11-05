Metavance
---

Follow instructions on https://github.com/altf4/libmelee to setup libmelee

Some notes that are buried or not explained:
* Agent must be on port 1, I found that the sticks didn't work for any action on port 2. Currently not possible to run an agent on more than port 1.
* When executing actions on a given frame, you are looking for the falling edge of the previous frame
	* Fox multishine for example:
		* Shine on frame 1
		* Jump on frame 1 of jump squat => after frame 3 of kneebend
* Unsure if it is necessary to use melee.enums.ENUM or if melee.ENUM is okay, documentation unclear


The [SLP Dataset](https://drive.google.com/file/d/1ab6ovA46tfiPZ2Y3a_yS1J3k3656yQ8f/view?usp=sharing) is required for the initial training setup. It needs to be placed in or linked to dataset/slp

