# Some documentation on Agents, Observation Spaces, and Action Spaces
This will be an intermediary until there is a need to make better docs. Currently, these classes are fairly straightforward and will not need tons of explanation. 

## Agents
Agents should inherit from at least the base `Agent` class. If your agent needs to choose different characters, inherit from the `AgentChooseCharacter` class and pass the correct enum as a parameter on initialization. Either way, make sure the `character` attribute is not `None`. 

Agents should always implement the `act` method. Act requires two parameters - an observation (from the observation space) and the set of available actions (the action space). Note that `act` does not return the action but just sets the `action` attribute. The `Random` agent and the `Shine` agent are useful to seeing how the action and observation spaces are used. 

## Observation Space
Observation spaces give agents information about the world around them. melee-env's `ObservationSpace` class provides a convenient way to translate libmelee's `gamestate` into a matrix data to be consumed by agents. `ObservationSpace.__call__` consumes libmelee's gamestate, and this function must return a numpy array with shape [P, C], where P is the number of players and C is the number of observed attributes (channels). Ideally this form is perfect for sending directly to popular learning frameworks, like TensorFlow or PyTorch, but is still flexible enough for other usage. See the example `ObservationSpace` in `util.py`. 

## Action Space
Action spaces provide an interface for agents to interact with their environment. An action space is essentially a list of possible actions. Since dolphin is designed to read inputs from a standard controller, we must map actions to controller inputs. libmelee implements controller actions, so we only need to know what actions we care about. Please refer to the example `ActionSpace` in `util.py`. 

### Control State
Note that if you choose to implement your own action state, you will also need to write a ControlState class that consumes your actions and is able to execute them on the controller. See `ControlState` in `util.py` for more. 