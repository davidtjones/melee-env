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

So an action will be a vector:

[ A, B, X, Y, Z, LT, RT, CS_X, CS_Y, MS_X, MS_Y ]

In addition to this encoding, there needs to be an easily accessible view into
the current state for the game. 

"""

import numpy as np
import melee

class ControlState:
    def __init__(self, state):
        self.state = state
        self.button_order = [
            melee.enums.Button.BUTTON_A,
            melee.enums.Button.BUTTON_B,
            melee.enums.Button.BUTTON_X,
            melee.enums.Button.BUTTON_Y,
            melee.enums.Button.BUTTON_Z]

    def execute(self, controller):
        for i, button in enumerate(self.button_order):
            if self.state[i] > 0:
                controller.press_button(button)
            else:
                controller.release_button(button)
        
        controller.press_shoulder(melee.enums.Button.BUTTON_L, self.state[5])
        controller.press_shoulder(melee.enums.Button.BUTTON_R, self.state[6])
        
        controller.tilt_analog_unit(melee.enums.Button.BUTTON_C, 
                                    self.state[7], self.state[8])

        controller.tilt_analog_unit(melee.enums.Button.BUTTON_MAIN, 
                                    self.state[9], self.state[10]) 
        controller.flush()

class ActionSpace:
    def __init__(self):
        self.button_space = np.array([0.0, 1.0])
        self.shoulder_space = np.array([0.0,          # none
                                        0.25,         # light press
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

        # Action space size is the length of the "action vector." Four buttons
        #   plus two shoulders plus four stick axes is 10.
        self.size = 10

    def sample_main_stick(self):
        return self.stick_space_circle[np.random.choice(len(self.stick_space_circle))]

    def sample_c_stick(self):
        return self.c_stick_space[np.random.choice(len(self.c_stick_space))]

    def sample_button(self, size=1):
        return np.random.choice(self.button_space, size=size)

    def sample_shoulder_trigger(self, size=1):
        return np.random.choice(self.shoulder_space, size=size)

    def generate_random_control_state(self):
        # There are seven buttons, the cstick, two triggers, and the main stick.
        #   Since this sampling is uniform, certain actions will be far more
        #   likely than others, e.g., smash attacks on the c-stick
        buttons = self.sample_button(7)
        c_stick = self.sample_c_stick()
        shoulder_l = self.sample_shoulder_trigger()
        shoulder_r = self.sample_shoulder_trigger()
        m_stick = self.sample_main_stick()
        control_state = np.concatenate((buttons, shoulder_l, shoulder_r, c_stick, m_stick))

        return ControlState(control_state)
        
        
