Some documentation on Agents, Observation Spaces, and Action Spaces
---
This will be an intermediary until there is a need to make better docs. Currently, these classes are fairly straightforward and will not need tons of explanation. 

## Agents
Agents should inherit from at least the base `Agent` class. If your agent needs to choose different characters, inherit from the `AgentChooseCharacter` class and pass the correct enum as a parameter on initialization. Either way, make sure the `character` attribute is not `None`, otherwise the game won't be able to choose a character for your agent. 

#### The `act` Method
Agents should always implement the `act` method. `act` takes the current gamestate. The code below is a minimal agent example which serves as a great starting point. 

```python
class MyNewAgent(Agent):
	def __init__(self, args):
		super().__init__()
		# unique attributes, data here

	def act(self, gamestate):
		# logic that dictates the next action. Make sure to set self.action.
		self.action = action  
```

From here, there is a lot of freedom in what you can do next.

##### Non-Learning Agents
 You are free to manipulate the controller, and the current control input will be executed on the next call to `env.step()`. The `Shine` agent provides a good demonstration on how this should look. Here is the `act` method from `Shine`: 
```python
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
```

##### Learning Agents
Alternatively, if you are developing a learning agent, you may wish to utilize an action space and/or an observation space. `melee-env` provides the `Rest` agent, which uses its own action and observation spaces: 
```python
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
		...
```
Notice how the action and observation spaces are defined in `__init__`. Then, the gamestate is converted into an observation through the decorator @from_observation_space and the agent's chosen action is converted to control inputs through the @from_action_space decorator. 

Lastly, agents must occupy ports sequentially starting at port 1. Currently, there are no plans to support every port configuration. Be careful if using the `Human` agent - you don't want to press start before you have selected a character, or the environment may crash. 

## Action and Observation Spaces
To provide the utmost flexibilty, melee-env does not include the action space and observation space as part of the environment itself (in contrast to OpenAI's Gym). Instead, the agent should manage their own action and observation spaces. This allows for multiple agents to run through melee-env simultaneously, since every agent is given the unaltered gamestate as input. While it may be too resource-intensive to run a 4-player game with heavy AI code, it is not beyond the realm of possiblity to run a 1v1 match against two AI. This provides a convenient way to benchmark performance for you own agent.

### Action Space
The goal of an action space is to provide an autonmous agent with free reign over what action it is allowed to pick. Ultimately, this is just a list of possible actions. `melee-env` provides a sample action-space that defines a minimal yet robust set of actions. You are free to define and use your own action space with melee-env. Note that to use the decorator `from_action_space`, you should implement the `__call__` method, which will take the index to a given action in the action space. `from_action_space` then converts this into real control inputs. See `ActionSpace` and `from_action_space` in util.py for more.

#### Control State
Note that if you choose to implement your own action state, you will also need to write a ControlState class that consumes your actions and is able to execute them on the agent's controller. See `ControlState` in util.py for an example. 

### Observation Space
The goal of an observation space is to extract information from the agent's world and to transform it into some usable form. For most machine-learning/deep learning frameworks, the numpy array serves as the base structure for this. `melee-env` provides a minimal observation space that is used with the `Rest` agent. Don't forget to reset your observation space between episodes.

#### 3 and 4 player games
Observation spaces can be somewhat tricky, as slippi completely stops reporting on players that have been defeated after 60 frames. This may not be a problem if you only plan to only run 1v1 environments. The sample Observation Space in `util.py` does contain some code to enable agents to maintain their observations in FFA-style matches. I'm unsure if this is the best possible method for this, but this does seem to work:
```python
class ObservationSpace:
    def __init__(self):
        self.previous_observation = np.empty(0)
        self.current_frame = 0
        self.intial_process_complete = False
		...

	def __call__(self, gamestate):
		...
		observation = something
		...
        if self.current_frame < 85 and not self.intial_process_complete:
            self.players_defeated_frames = np.array([0] * len(observation))
            self.intial_process_complete = True

        defeated_idx = np.where(observation[:, -1] == 0)
        self.players_defeated_frames[defeated_idx] += 1

        if len(observation) < len(self.previous_observation):
            rows_to_insert = np.where(self.players_defeated_frames >= 60)
            for row in rows_to_insert:
                observation = np.insert(observation, row, self.previous_observation[row], axis=0) 

		...
		self.previous_observation = observation
```