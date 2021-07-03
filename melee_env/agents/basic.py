from abc import ABC, abstractmethod
from melee import enums
import numpy as np

def is_defeated(f):
# libmelee/slippi reports defeated state for 60 frames, then completely 
#   drops the player from reporting. We need to know when the player is defeated
#   so that a row can be added back to the observation list to keep the size
#   consistent. This helps avoid certain wonky behavior. 
    def wrapper(self, *args):
        if not self.defeated and args[0][self.port-1, -1] != 0:
            return f(self, *args) 
    return wrapper

class Agent(ABC):
    def __init__(self):
        self.agent_type = None
        self.controller = None
        self.port = None
        self.action = None
        self.press_start = False
    
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
    def act():
        pass


class CPU(AgentChooseCharacter):
    def __init__(self, character, lvl):
        super().__init__(character)
        self.agent_type = "CPU"
        if not 1 <= lvl <= 9:
            raise ValueError(f"CPU Level must be 1-9. Got {lvl}")
        self.lvl = lvl
    
    @is_defeated  
    def act():
        pass


class Random(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)
        self.agent_type = "AI"
        
    @is_defeated
    def act(self, observation, action_space):
        #if not self.is_defeated(observation):
        action = action_space.sample()
        self.action = action


class Shine(Agent):
    # refer to action_space.py
    def __init__(self):
        super().__init__()
        self.agent_type = "AI"
        self.character = enums.Character.FOX
    
    @is_defeated
    def act(self, observation, action_space):
        #if not self.is_defeated(observation):
        action = 0  # none 
        fox_state = observation[self.port-1][2]
        fox_frames = observation[self.port-1][3]
        fox_hitstun = observation[self.port-1][4]

        if (fox_state == enums.Action.STANDING.value or 
            fox_state == enums.Action.CROUCH_START.value):
            action = 5  # crouch

        if fox_state == enums.Action.CROUCHING.value:
            action = 23  # down-B (shine)

        if fox_state == enums.Action.KNEE_BEND.value and fox_frames == 3:
                action = 23  # shine again on frame 3 of knee bend.

        if (fox_state == enums.Action.DOWN_B_GROUND.value or 
            fox_state == enums.Action.DOWN_B_GROUND_START.value):
            action = 10  # tap jump

        if fox_hitstun > 0:
            action = 0  # don't do crazy things while in hitstun

        self.action = action

class Rest(Agent):
    # adapted from AltF4's tutorial video: https://www.youtube.com/watch?v=1R723AS1P-0
    # This agent will target the nearest player, move to them, and rest
    def __init__(self):
        super().__init__()
        self.agent_type = "AI"
        self.character = enums.Character.JIGGLYPUFF

    @is_defeated
    def act(self, observation, action_space):
        # find the nearest player
        curr_position = observation[self.port-1, :2]
        positions_centered = observation[:, :2] - curr_position

        # distance formula
        distances = np.sqrt(np.sum(positions_centered**2, axis=1))
        closest = np.argsort(np.sqrt(np.sum(positions_centered**2, axis=1)))[1]  # this could be dangerous

        if distances[closest] < 4:
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
