import numpy as np
import melee


class ObservationSpace:
    def __init__(self):
        self.current_frame = 0
        self.done = False
        self.previous_gamestate = None
        self.current_gamestate = None

    def _reset(self):
        self.current_frame = 0
        self.done = False
        self.previous_gamestate = None
        self.current_gamestate = None

    def get_stocks(self):
        stocks = [self.current_gamestate.players[i].stock for i in list(self.current_gamestate.players.keys())]
        return np.array([stocks]).T  # players x 1
    
    def get_actions(self):
        actions = [self.current_gamestate.players[i].action.value for i in list(self.current_gamestate.players.keys())]
        action_frames = [self.current_gamestate.players[i].action_frame for i in list(self.current_gamestate.players.keys())]
        hitstun_frames_left = [self.current_gamestate.players[i].hitstun_frames_left for i in list(self.current_gamestate.players.keys())]
        
        return np.array([actions, action_frames, hitstun_frames_left]).T # players x 3

    def get_positions(self):
        x_positions = [self.current_gamestate.players[i].x for i in list(self.current_gamestate.players.keys())]
        y_positions = [self.current_gamestate.players[i].y for i in list(self.current_gamestate.players.keys())]

        return np.array([x_positions, y_positions]).T  # players x 2

    def __call__(self, gamestate):
        """ pull out relevant info from gamestate """
        self.current_gamestate = gamestate
        self.current_frame +=1 
        total_reward = 0
        info = None
        
        positions = self.get_positions()
        actions = self.get_actions()
        stocks = self.get_stocks()



        # this is fancy one liner that just says if the player(s) with the 
        #   fewest stocks sum to zero, the game is over. Doesn't cover teams.
        # self.done = not self.current_observation[np.argsort(self.current_observation[:, -1])][::-1][1:, -1]
        
        if self.current_frame > 85 and not self.done:
            # reward/penalize based on delta damage/stocks
            # +- 1 for stocks taken/lost
            # total_reward += (stocks[0][1])
            # total_reward -= (stocks[0][0])

            # # if stocks change, don't reward for going back to 0 damage
            # # assumption: you can't lose more than one stock on a given frame
            # total_reward -= (percents[0][0] * (1^stocks[0][0])) * .01
            # total_reward += (percents[0][1] * (1^stocks[0][1])) * .01
            total_reward = 0

        if self.current_gamestate is not None:
            self.previous_gamestate = self.current_gamestate

        
        observation = np.concatenate((positions, actions, stocks), axis=1)

        return observation, total_reward, self.done, info


class ActionSpace:
    def __init__(self):
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

        # self.action_space will look like this, where the first two columns
        #   represent the control stick's position, and the final column is the 
        #   currently depressed button. 

        # ACT  Left/Right    Up/Down      Button
        # ---  ------        ------       ------
        # 0   [ 0.        ,  0.        ,  0. (NO-OP)] Center  ---
        # 1   [ 0.        ,  1.        ,  0.        ] Up         |
        # 2   [ 0.70710678,  0.70710678,  0.        ] Up/Right   |
        # 3   [ 1.        ,  0.        ,  0.        ] Right      |
        # 4   [ 0.70710678, -0.70710678,  0.        ] Down/Right |- these repeat
        # 5   [ 0.        , -1.        ,  0.        ] Down       |
        # 6   [-0.70710678, -0.70710678,  0.        ] Down/Left  |
        # 7   [-1.        ,  0.        ,  0.        ] Left       |
        # 8   [-0.70710678,  0.70710678,  0.        ] Up/Left  ---
        # 9   [ 0.        ,  0.        ,  1. (A)    ] 
        # 10  [ 0.        ,  1.        ,  1.        ] 
        # 11  [ 0.70710678,  0.70710678,  1.        ]
        # 12  [ 1.        ,  0.        ,  1.        ]
        # 13  [ 0.70710678, -0.70710678,  1.        ]
        # 14  [ 0.        , -1.        ,  1.        ]
        # 15  [-0.70710678, -0.70710678,  1.        ]
        # 16  [-1.        ,  0.        ,  1.        ]
        # 17  [-0.70710678,  0.70710678,  1.        ]
        # 18  [ 0.        ,  0.        ,  2. (B)    ] 
        # 19  [ 0.        ,  1.        ,  2.        ]
        # 20  [ 0.70710678,  0.70710678,  2.        ]
        # 21  [ 1.        ,  0.        ,  2.        ]
        # 22  [ 0.70710678, -0.70710678,  2.        ]
        # 23  [ 0.        , -1.        ,  2.        ]
        # 24  [-0.70710678, -0.70710678,  2.        ]
        # 25  [-1.        ,  0.        ,  2.        ]
        # 26  [-0.70710678,  0.70710678,  2.        ]
        # 27  [ 0.        ,  0.        ,  3. (Z)    ] 
        # 28  [ 0.        ,  1.        ,  3.        ]
        # 29  [ 0.70710678,  0.70710678,  3.        ]
        # 30  [ 1.        ,  0.        ,  3.        ]
        # 31  [ 0.70710678, -0.70710678,  3.        ]
        # 32  [ 0.        , -1.        ,  3.        ]
        # 33  [-0.70710678, -0.70710678,  3.        ]
        # 34  [-1.        ,  0.        ,  3.        ]
        # 35  [-0.70710678,  0.70710678,  3.        ] 
        # 36  [ 0.        ,  0.        ,  4. (R)    ] 
        # 37  [ 0.        ,  1.        ,  4.        ]
        # 38  [ 0.70710678,  0.70710678,  4.        ]
        # 39  [ 1.        ,  0.        ,  4.        ]
        # 40  [ 0.70710678, -0.70710678,  4.        ]
        # 41  [ 0.        , -1.        ,  4.        ]
        # 42  [-0.70710678, -0.70710678,  4.        ]
        # 43  [-1.        ,  0.        ,  4.        ]
        # 45  [-0.70710678,  0.70710678,  4.        ]

        self.size = self.action_space.shape[0]

    def sample(self):
        return np.random.choice(self.size)

    def __call__(self, action):
        if action > self.size - 1:
            exit("Error: invalid action!")

        return ControlState(self.action_space[action])


class ControlState:
    def __init__(self, state):
        self.state = state
        self.buttons = [
            False,
            melee.enums.Button.BUTTON_A,
            melee.enums.Button.BUTTON_B,
            melee.enums.Button.BUTTON_Z,
            melee.enums.Button.BUTTON_R]

    def execute(self, controller):
        controller.release_all()      
        if self.state[2]:             # only press button if not no-op
            if self.state[2] != 4.0:  # special case for r shoulder
                controller.press_button(self.buttons[int(self.state[2])]) 
            else:
                controller.press_shoulder(melee.enums.Button.BUTTON_R, 1)
        
        controller.tilt_analog_unit(melee.enums.Button.BUTTON_MAIN, 
                                    self.state[0], self.state[1])
