from abc import ABC, abstractmethod
from melee import enums
import numpy as np


def is_defeated(f):
# libmelee/slippi reports defeated state for 60 frames, then completely 
#   drops the player from reporting. We need to know when the player is defeated
#   so that a row can be added back to the observation list to keep the size
#   consistent. This helps avoid certain wonky behavior. 
    def wrapper(self, *args):
        self.self_observation = args[0][self.port-1]
        if not self.defeated and self.self_observation[-1] != 0:
            return f(self, *args)
        elif not self.defeated and self.self_observation[-1] == 0:
            self.defeated = True
            print(f"{self} was defeated")
    return wrapper

class Agent(ABC):
    def __init__(self):
        self.agent_type = "AI"
        self.controller = None
        self.port = None
        self.action = 0
        self.press_start = False
        self.self_observation = None
    
    @abstractmethod
    def act(self):
        pass

class AgentChooseCharacter(Agent):
    def __init__(self, character):
        super().__init__()
        self.character = character
        

class Human(Agent):
    def __init__(self):
        super().__init__()
        self.agent_type = "HMN"
    
    @is_defeated
    def act(self, observation, action_space):
        pass


class CPU(AgentChooseCharacter):
    def __init__(self, character, lvl):
        super().__init__(character)
        self.agent_type = "CPU"
        if not 1 <= lvl <= 9:
            raise ValueError(f"CPU Level must be 1-9. Got {lvl}")
        self.lvl = lvl
    
    @is_defeated  
    def act(self, observation, action_space):
        pass


class NOOP(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)

    @is_defeated
    def act(self, observation, action_space):
        self.action = 0


class Random(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)
        
    @is_defeated
    def act(self, observation, action_space):
        #if not self.is_defeated(observation):
        action = action_space.sample()
        self.action = action


class Shine(Agent):
    # refer to action_space.py
    def __init__(self):
        super().__init__()
        self.character = enums.Character.FOX
    
    @is_defeated
    def act(self, observation, action_space):
        #if not self.is_defeated(observation):
        action = 0  # none 
        state, frames, hitstun = observation[self.port-1][2:5]

        if (state == enums.Action.STANDING.value or 
            state == enums.Action.CROUCH_START.value):
            action = 5  # crouch

        if state == enums.Action.CROUCHING.value:
            action = 23  # down-B (shine)

        if state == enums.Action.KNEE_BEND.value and frames == 3:
                action = 23  # shine again on frame 3 of knee bend.

        if (state == enums.Action.DOWN_B_GROUND.value or 
            state == enums.Action.DOWN_B_GROUND_START.value):
            action = 10  # tap jump

        if hitstun > 0:
            action = 0  # don't do crazy things while in hitstun

        self.action = action


class Rest(Agent):
    # adapted from AltF4's tutorial video: https://www.youtube.com/watch?v=1R723AS1P-0
    # This agent will target the nearest player, move to them, and rest
    def __init__(self):
        super().__init__()
        self.character = enums.Character.JIGGLYPUFF

    @is_defeated
    def act(self, observation, action_space):
        # In order to make Rest-bot work for any number of players, it needs to 
        #   select a target. In this code, a target is selected by identifying
        #   the closest player who is not currently defeated/respawning. We 
        #   could use stage boundaries as defined in melee.stages but that would
        #   limit rest-bot to only working on tournament-legal stages. 

        curr_position = observation[self.port-1, :2]
        positions_centered = observation[:, :2] - curr_position

        # distance formula
        distances = np.sqrt(np.sum(positions_centered**2, axis=1))
        closest_sort = np.argsort(np.sqrt(np.sum(positions_centered**2, axis=1)))  

        actions = observation[:, 2]
        actions_by_closest = actions[closest_sort]

        # select closest player who isn't dead
        closest = 0
        for i in range(len(observation)):
            if actions_by_closest[i] >= 14 and i != 0:
                closest = closest_sort[i]
                break

        if closest == self.port-1:  # nothing to target
            action = 0

        elif distances[closest] < 4:
            action = 23  # Rest

        else:  
            # Directing the bots movement is tricky since we use the action 
            #   space. We can only input one command at a time, so it is 
            #   neccessary to prioritize jumping or movement. Also, we must
            #   tell the bot to re-input buttons occassionally so it doesn't
            #   get stuck. 

            if np.abs(positions_centered[closest, 0]) < np.abs(positions_centered[closest, 1]):
                # closer in X than in Y - prefer jump
            
                if observation[closest, 1] > curr_position[1]:
                    if self.action == 1:
                        action = 0  # re-input jump
                    else:
                        action = 1
                else:
                    if self.action == 5:
                        action = 0
                    else:
                        action = 5  # reinput down to fall through platforms
            else:
                # closer in Y than in X - prefer run/drift
                if observation[closest, 0] < curr_position[0]:
                    action = 7  # move left
                else:
                    action = 3  # move right

        self.action = action
