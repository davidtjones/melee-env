from abc import ABC, abstractmethod
from melee import enums

class Agent(ABC):
    def __init__(self):
        self.agent_type = None
        self.controller = None
        self.port = None
        self.action = None
        self.defeated = False

    def _is_defeated(self, observation):
        if self.defeated:
            return True
        
        elif observation[3] == 0 and not self.defeated:
            self.defeated = True
            self.action = 0
            print(f"{self} got beat")
            return True

        else:
            return False

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
        
    def act():
        pass


class CPU(AgentChooseCharacter):
    def __init__(self, character, lvl):
        super().__init__(character)
        self.agent_type = "CPU"
        if not 1 <= lvl <= 9:
            raise ValueError(f"CPU Level must be 1-9. Got {lvl}")
        self.lvl = lvl
        
    def act():
        pass


class Random(AgentChooseCharacter):
    def __init__(self, character):
        super().__init__(character)
        self.agent_type = "AI"
           
    def act(self, observation, action_space):
        if not self._is_defeated(observation):
            action = action_space.sample()
            self.action = action


class Shine(Agent):
    # refer to action_space.py
    def __init__(self):
        super().__init__()
        self.agent_type = "AI"
        self.character = enums.Character.FOX
        
    def act(self, observation, action_space):
        # lib/melee reports defeated state for 60 frames, then completely drops
        #   the player from reporting
        if not self._is_defeated(observation):
            action = 0  # none 

            if (observation[0] == enums.Action.STANDING.value or 
                observation[0] == enums.Action.CROUCH_START.value):
                action = 5  # crouch

            if observation[0] == enums.Action.CROUCHING.value:
                action = 23  # down-B (shine)

            if observation[0] == enums.Action.KNEE_BEND.value and observation[1] == 3:
                    action = 23  # shine again on frame 3 of knee bend.

            if (observation[0] == enums.Action.DOWN_B_GROUND.value or 
                observation[0] == enums.Action.DOWN_B_GROUND_START.value):
                action = 10  # tap jump

            if observation[2] > 0:
                action = 0  # don't do crazy things while in hitstun
            
            self.action = action
