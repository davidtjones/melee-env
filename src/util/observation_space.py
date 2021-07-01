import numpy as np
import code

class ObservationSpace:
    def __init__(self):
        self.size = 18  # better way to set this?
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
        stocks = [self.current_gamestate.player[i].stock for i in list(self.current_gamestate.player.keys())]
        return np.array([stocks]).T #playersx1
    
    def get_actions(self):
        actions = [self.current_gamestate.player[i].action.value for i in list(self.current_gamestate.player.keys())]
        action_frames = [self.current_gamestate.player[i].action_frame for i in list(self.current_gamestate.player.keys())]
        hitstun_frames_left = [self.current_gamestate.player[i].hitstun_frames_left for i in list(self.current_gamestate.player.keys())]
        
        return np.array([actions, action_frames, hitstun_frames_left]).T # playersx3
        
    def __call__(self, gamestate):
        """ pull out relevant info from gamestate """
        self.current_gamestate = gamestate
        self.current_frame +=1 
        total_reward = 0
        info = None
        
        actions = self.get_actions()
        stocks = self.get_stocks()

        # if 0 <= actions[0][0] <= 10:  # DEAD_DOWN, DEAD_LEFT ... 
        #     info = "dead"
        
        # self.done = not (bool(stocks[1][0]) or bool(stocks[1][1]))
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

        
        observation = np.concatenate((actions, stocks), axis=1)

        return observation, total_reward, self.done, info