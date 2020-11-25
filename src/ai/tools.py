"""
So what is really needed is an encoding from ControllerState to some vector-
respresentation of the controller. I.e., if given a vector of length N, 
assigning values to that vector directly corresponds to a controller state.

This can then be used as input/output to the model, etc. 

There are 10 buttons, 5 of which probably shouldn't be used the AI (dpad, start)
for a total of 5 buttons with binary values (A, B, X, Y, Z). 

Furthermore the shoulder buttons can be divided into two states: hard press 
and light press. Hard press is a full 255 and light press should be the minimum 
amount of pressure such that light shield is activated, with an additional 0
pressure meaning nothing. 

Then there are two analog control sticks. I think the analog sticks are likely
8 bits on both axes but that is an insane level of detail for a game 
where only a few levels of detail are needed. Libmelee specifically allows for
floating point representations on these with ranges of [0, 1] or [-1, 1]. I 
like the [-1, 1] representation as I think it is the most clear, 0 being 
no movement. 

The c-stick has no other real function except for the full cardinal directions.

In addition to this encoding, there needs to be an easily accessible view into
the current state for the game. 

"""

import numpy as np
import melee


class ActionSpace:
    def __init__(self):
        self.button_space = np.array([0.0, 1.0])
        self.shoulder_space = np.array([0.0,          # none
                                        # 0.1,         # light press
                                        1.0])         # hard press    
        
        self.c_stick_space = np.array([[0.0, 0.0],    # center
                                       [1.0, 0.0],    # right
                                       [0.0, -1.0],   # down
                                       [-1.0, 0.0],   # left
                                       [0.0, 1.0]])   # up

        
        # The main control stick is slightly harder as there isn't a simple
        #   square stick box, so some calculation is needed to find legal 
        #   values. Also of note, the space of values of the stick needs to
        #   include no-op, so an odd value must be used on the number of 
        #   steps. 
        self.stick_values = np.linspace(-1, 1, (2**3)-1)
        
        # create tuples of all possible stick values:
        self.stick_space_square = np.array(
            np.meshgrid(self.stick_values, self.stick_values)).T.reshape(-1, 2)

        # These contain illegal values in a circular stick box, you can never
        #   achieve (1,1), for example. For any values a and b,  a^2 + b^2 > 1 
        #   are thus illegal. 

        dist = np.sqrt(
            self.stick_space_square[:, 0]**2 + self.stick_space_square[:, 1]**2)
        legal_indices = np.where(dist <= 1)

        self.stick_space_circle = self.stick_space_square[legal_indices]

        mid = np.sqrt(2)/2

        self.stick_space_reduced = np.array([[0.0, 0.0], # no op
                                             [0.0, 1.0],
                                             [mid, mid],
                                             [1.0, 0.0],
                                             [mid, -mid],
                                             [0.0, -1.],
                                             [-mid, -mid],
                                             [-1., 0.0],
                                             [-mid, mid]])

        self.button_space_reduced = np.array([0., 1., 2., 3., 4.])

        # Action space size is total number of possible actions. In this case,
        #    is is all possible main stick positions * all c-stick positions *
        #    all the buttons. A normal controller has ~51040 possible main stick 
        #    positions. Each trigger has 255 positions. The c-stick can be 
        #    reduced to ~5 positions. Finally, if all buttons can be pressed
        #    in any combination, that results in 32 combinations. Not including
        #    the dpad or start button, that is 51040 * 5 * 255 * 2 * 32 which 
        #    is a staggering 4.165 billion possible control states. 

        # Given this, it is reasonable to reduce this. In the above class, the 
        #    main stick has been reduced to the 8 cardinal positions plus the 
        #    center (no-op). Only A, B, Z, and R are used, as these correspond
        #    to major in-game functions (attack, special, grab, shield). Every
        #    action can theoretically be performed with just these buttons. A 
        #    final "button" is added for no-op. 
        #
        #    Action space = 9 * 5 = 45 possible actions. 

        self.action_space = np.zeros((self.stick_space_reduced.shape[0] * self.button_space_reduced.shape[0], 3))

        for button in self.button_space_reduced:
            self.action_space[int(button)*9:(int(button)+1)*9, :2] = self.stick_space_reduced
            self.action_space[int(button)*9:(int(button)+1)*9, 2] = button

        self.size = self.action_space.shape[0]


    def __call__(self, action):
        if action > self.size - 1:
            exit("Error: invalid action!")

        return ControlState(self.action_space[action])

        
class ControlState:
    def __init__(self, state):
        self.state = state
        self.buttons = [
            melee.enums.Button.BUTTON_A,
            melee.enums.Button.BUTTON_B,
            melee.enums.Button.BUTTON_R,
            melee.enums.Button.BUTTON_Z]

    def execute(self, controller):
        controller.release_all()      # reset everything real quick
        if self.state[2] != 0.0:      # no-op
            if self.state[2] != 3.0:  # R shoulder
                controller.press_button(self.buttons[int(self.state[2])-1]) 
            else:
                controller.press_shoulder(melee.enums.Button.BUTTON_R, 1)
        
        controller.tilt_analog_unit(melee.enums.Button.BUTTON_MAIN, 
                                    self.state[0], self.state[1]) 
if __name__ == "__main__":
    import code
    asp = ActionSpace()
    code.interact(local=locals())
