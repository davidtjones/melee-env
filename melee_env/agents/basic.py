from abc import ABC, abstractmethod
from melee import enums
import numpy as np
from melee_env.agents.util import *
import code

class Agent(ABC):
    def __init__(self):
        self.agent_type = "AI"
        self.controller = None
        self.port = None  # this is also in controller, maybe redundant?
        self.action = 0
        self.press_start = False
        self.self_observation = None
        self.current_frame = 0

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
    
    def act(self, gamestate):
        pass


class CPU(AgentChooseCharacter):
    def __init__(self, character, lvl):
        super().__init__(character)
        self.agent_type = "CPU"
        if not 1 <= lvl <= 9:
            raise ValueError(f"CPU Level must be 1-9. Got {lvl}")
        self.lvl = lvl
    
    def act(self, gamestate):
        pass


class NOOP(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)

    def act(self, gamestate):
        self.action = 0


class Random(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)
        self.action_space = ActionSpace()
    
    @from_action_space
    def act(self, gamestate):
        action = self.action_space.sample()
        return action

class Shine(Agent):
    def __init__(self):
        super().__init__()
        self.character = enums.Character.FOX
    
    def act(self, gamestate):
        state = gamestate.players[self.port].action
        frames = gamestate.players[self.port].action_frame
        hitstun = gamestate.players[self.port].hitstun_frames_left
        
        if state in [enums.Action.STANDING]:
            self.controller.tilt_analog_unit(enums.Button.BUTTON_MAIN, 0, -1)

        if (state == enums.Action.CROUCHING or (
            state == enums.Action.KNEE_BEND and frames == 3)):
            self.controller.release_button(enums.Button.BUTTON_Y)
            self.controller.press_button(enums.Button.BUTTON_B)

        if state in [enums.Action.DOWN_B_GROUND]:
            self.controller.release_button(enums.Button.BUTTON_B)
            self.controller.press_button(enums.Button.BUTTON_Y)

        if hitstun > 0:
            self.controller.release_all()

class Rest(Agent):
    # adapted from AltF4's tutorial video: https://www.youtube.com/watch?v=1R723AS1P-0
    # This agent will target the nearest player, move to them, and rest
    def __init__(self):
        super().__init__()
        self.character = enums.Character.JIGGLYPUFF

        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()
        self.action = 0
        
    @from_action_space       # translate the action from action_space to controller input
    @from_observation_space  # convert gamestate to an observation
    def act(self, observation):
        observation, reward, done, info = observation

        # In order to make Rest-bot work for any number of players, it needs to 
        #   select a target. A target is selected by identifying the closest 
        #   player who is not currently defeated/respawning.  
        curr_position = observation[self.port-1, :2]
        try:
            positions_centered = observation[:, :2] - curr_position
        except:
            code.interact(local=locals())

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

        return self.action
