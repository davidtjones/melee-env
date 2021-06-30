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
        # return a tuple (p1 stocks lost, p2 stocks lost)
        current = np.array([
            self.current_gamestate.player[1].stock, 
            self.current_gamestate.player[2].stock])

        if self.previous_gamestate is not None:
            previous = np.array([
                self.previous_gamestate.player[1].stock, 
                self.previous_gamestate.player[2].stock])

            diff = previous - current  # stocks go down
        else:
            diff = np.array([0, 0])
        return np.array([diff, current])

    def get_percents(self):
        # return a array [(damage done, damage taken)]
        current = np.array([
            self.current_gamestate.player[1].percent,
            self.current_gamestate.player[2].percent])
        if self.previous_gamestate is not None:
            previous = np.array([
                self.previous_gamestate.player[1].percent,
                self.previous_gamestate.player[2].percent])
        
            diff = current - previous  # percents go up
        else:
            diff = np.array([0, 0])

        return np.array([diff, current])


    def get_positions(self):
        facing = (self.current_gamestate.player[1].facing, 
                  self.current_gamestate.player[2].facing)

        x = (self.current_gamestate.player[1].x, 
             self.current_gamestate.player[2].x)

        y = (self.current_gamestate.player[1].y, 
             self.current_gamestate.player[2].y)

        return np.array([facing, x, y])

    def get_actions(self):
        action = (self.current_gamestate.player[1].action.value, 
                  self.current_gamestate.player[2].action.value)

        action_frame = (self.current_gamestate.player[1].action_frame, 
                        self.current_gamestate.player[2].action_frame)
        
        return np.array([action, action_frame])
        
    def __call__(self, gamestate):
        """ pull out relevant info from gamestate """
        self.current_gamestate = gamestate
        self.current_frame +=1 
        total_reward = 0
        info = None
        
        stocks = self.get_stocks()        # 2x2
        percents = self.get_percents()    # 2x2 
        positions = self.get_positions()  # 3x2
        actions = self.get_actions()      # 2x2 

        # after calling flatten:
        # [p1_stocks, p1_stock_d, p2_stocks, p2_stock_d, 
        #  p1_percent, p1_percent_d, p2_percent, p2_percent_d,
        #  p1_facing, p2_facing, p1_x, p2_x, p1_y, p2_y, 
        #  p1_action, p2_action, p1_act_f, p2_act_f]
        #
        # categorical feature indices: p1_facing (8), p2_facing(9), p1_action(14), p2_action(15)

        if 0 <= actions[0][0] <= 10:  # DEAD_DOWN, DEAD_LEFT ... 
            info = "dead"
        
        self.done = not (bool(stocks[1][0]) or bool(stocks[1][1]))
        if self.current_frame > 85 and not self.done:
            # reward/penalize based on delta damage/stocks

            # +- 1 for stocks taken/lost
            total_reward += (stocks[0][1])
            total_reward -= (stocks[0][0])

            # if stocks change, don't reward for going back to 0 damage
            # assumption: you can't lose more than one stock on a given frame
            total_reward -= (percents[0][0] * (1^stocks[0][0])) * .01
            total_reward += (percents[0][1] * (1^stocks[0][1])) * .01


        if self.current_gamestate is not None:
            self.previous_gamestate = self.current_gamestate

        
        observation = np.concatenate((stocks, percents, positions, actions))


        return observation, total_reward, self.done, info