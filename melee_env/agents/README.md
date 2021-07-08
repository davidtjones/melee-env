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
Alternatively, if you are developing a learning agent, you may wish to utilize an action space and/or an observation space. To provide the utmost flexibilty, melee-env does not include the action space and observation space as part of the environment itself (in contrast to OpenAI's Gym). Instead, the agent should manage their own action and observation spaces. This allows for multiple agents to run through melee-env simultaneously, since every agent is given the unaltered gamestate as input. While it may be too resource-intensive to run a 4-player game with heavy AI code, it is not beyond the realm of possiblity to run a 1v1 match against two AI. This provides a convenient way to benchmark performance for you own agent. `melee-env` provides the `Rest` agent, which uses its own action and observation spaces: 
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

## Observation Space
Observation spaces give agents information about the world around them. melee-env's `ObservationSpace` class provides a convenient way to translate libmelee's `gamestate` into a matrix data to be consumed by agents. `ObservationSpace.__call__` consumes libmelee's gamestate, and this function must return a numpy array with shape [P, C], where P is the number of players and C is the number of observed attributes (channels). Ideally this form is perfect for sending directly to popular learning frameworks, like TensorFlow or PyTorch, yet still flexible enough for other usage.

**Stocks are required to be in the observation**. Since stocks impact the game state, I have adopted the convention that stocks must be included in the observation and must be the last channel, in player order. See the example `ObservationSpace` in `util.py`. If you choose not to use stocks in your agent, you can use slicing to remove the stocks in the act method with observation[:, :-1].

## Action Space
Action spaces provide an interface for agents to interact with their environment. An action space is essentially a list of possible actions. Since dolphin is designed to read inputs from a standard controller, we must map actions to controller inputs. libmelee implements controller actions, so we only need to know what actions we care about. Please refer to the example `ActionSpace` in `util.py`. 

#### Control State
Note that if you choose to implement your own action state, you will also need to write a ControlState class that consumes your actions and is able to execute them on the controller. See `ControlState` in `util.py` for an example. 