Metavance
---

Follow instructions on https://github.com/altf4/libmelee to setup libmelee

Some notes that are buried or not explained:
* Agent must be on port 1, I found that the sticks didn't work for any action on port 2 (didn't try ports 3 or 4)
* When executing actions on a given frame, you are looking for the falling edge of the previous frame
	* Fox multishine for example:
		* Shine on frame 1
		* Jump on frame 1 of jump squat => after frame 3 of kneebend
* Unsure if it is necessary to use melee.enums.ENUM or if melee.ENUM is okay, documentation unclear


	

