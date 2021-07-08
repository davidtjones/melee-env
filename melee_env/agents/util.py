import numpy as np
import melee


class ObservationSpace:
    def __init__(self):
        self.previous_observation = np.empty(0)
        # self.current_gamestate = None
        self.curr_action = None
        self.player_count = None
        self.current_frame = 0
        self.intial_process_complete = False

    def set_player_keys(self, keys):
        self.player_keys = keys

    def get_stocks(self, gamestate):
        stocks = [gamestate.players[i].stock for i in list(gamestate.players.keys())]
        return np.array([stocks]).T  # players x 1
  
    def get_actions(self, gamestate):
        actions = [gamestate.players[i].action.value for i in list(gamestate.players.keys())]
        action_frames = [gamestate.players[i].action_frame for i in list(gamestate.players.keys())]
        hitstun_frames_left = [gamestate.players[i].hitstun_frames_left for i in list(gamestate.players.keys())]
        
        return np.array([actions, action_frames, hitstun_frames_left]).T # players x 3

    def get_positions(self, gamestate):
        x_positions = [gamestate.players[i].position.x for i in list(gamestate.players.keys())]
        y_positions = [gamestate.players[i].position.y for i in list(gamestate.players.keys())]

        return np.array([x_positions, y_positions]).T  # players x 2

    def __call__(self, gamestate):
        reward = 0
        info = None
        self.current_gamestate = gamestate
        self.player_count = len(list(gamestate.players.keys()))
        
        observation = np.concatenate((
            self.get_positions(gamestate), 
            self.get_actions(gamestate), 
            self.get_stocks(gamestate)), axis=1)


        if self.current_frame < 85 and not self.intial_process_complete:
            self.players_defeated_frames = np.array([0] * len(observation))
            self.intial_process_complete = True

        defeated_idx = np.where(observation[:, -1] == 0)
        self.players_defeated_frames[defeated_idx] += 1

        if len(observation) < len(self.previous_observation):
            rows_to_insert = np.where(self.players_defeated_frames >= 60)
            for row in rows_to_insert:
                observation = np.insert(observation, row, self.previous_observation[row], axis=0)            

        self.done = not np.sum(observation[np.argsort(observation[:, -1])][::-1][1:, -1])

        if self.current_frame > 85 and not self.done:
            # difficult to derive a reward function in a (possible) 4-player env
            # but you might define some reward function here
            # self.total_reward += reward
            reward = 0
        
        # previous observation will always have the correct number of players
        self.previous_observation = observation
        self.current_frame += 1

        if self.done:
            self._reset()

        return observation, reward, self.done, info

    def _reset(self):
        self.__init__()
        print("observation space got reset!")


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

    def __call__(self, controller):
        controller.release_all()      
        if self.state[2]:             # only press button if not no-op
            if self.state[2] != 4.0:  # special case for r shoulder
                controller.press_button(self.buttons[int(self.state[2])]) 
            else:
                controller.press_shoulder(melee.enums.Button.BUTTON_R, 1)
        
        controller.tilt_analog_unit(melee.enums.Button.BUTTON_MAIN, 
                                    self.state[0], self.state[1])

def from_observation_space(act):
    def get_observation(self, *args):
        gamestate = args[0]
        observation = self.observation_space(gamestate)
        return act(self, observation)
    return get_observation

def from_action_space(act):
    def get_action_encoding(self, *args):
        gamestate = args[0]
        action = act(self, gamestate)
        control = self.action_space(action)
        control(self.controller)
        return 
    return get_action_encoding