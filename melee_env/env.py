from melee_env.dconfig import DolphinConfig
import melee
from melee import enums
import numpy as np
    
class MeleeEnv:
    def __init__(self, 
        iso_path,
        players,
        action_space,
        observation_space,
        fast_forward=False, 
        blocking_input=False,
        ai_starts_game=False):

        self.d = DolphinConfig()
        self.d.set_ff(fast_forward)

        self.iso_path = iso_path
        self.players = players

        self.action_space = action_space 
        self.observation_space = observation_space

        self.blocking_input = blocking_input
        self.ai_starts_game = ai_starts_game

        self.gamestate = None


    def start(self):
        self.console = melee.Console(
            path=str(self.d.slippi_bin_path),
            dolphin_home_path=str(self.d.slippi_home)+"/",
            blocking_input=self.blocking_input)  # broken in 0.21.0

        # Configure Dolphin for the correct controller setup, add controllers
        for i in range(len(self.players)):
            curr_player = self.players[i]

            if curr_player.agent_type == "HMN":
                self.d.set_controller_type(i+1, enums.ControllerType.GCN_ADAPTER)
                curr_player.controller = melee.Controller(console=self.console, port=i+1, type=melee.ControllerType.GCN_ADAPTER)
                curr_player.port = i+1
            elif curr_player.agent_type in ["AI", "CPU"]:
                self.d.set_controller_type(i+1, enums.ControllerType.STANDARD)
                curr_player.controller = melee.Controller(console=self.console, port=i+1)
                self.menu_control_agent = i
                curr_player.port = i+1 
            else:  # no player
                self.d.set_controller_type(i+1, enums.ControllerType.UNPLUGGED)
        
        self.console.run(iso_path=self.iso_path)
        self.console.connect()


        [player.controller.connect() for player in self.players if player is not None]

        self.gamestate = self.console.step()
 
    def setup(self, stage):
        while True:
            self.gamestate = self.console.step()
            if self.gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
                for i in range(len(self.players)):
                    if self.players[i].agent_type == "AI":
                        melee.MenuHelper.choose_character(
                            character=self.players[i].character,
                            gamestate=self.gamestate,
                            controller=self.players[i].controller,
                            costume=i,
                            swag=False,
                            start=self.ai_starts_game)
                    if self.players[i].agent_type == "CPU":
                        melee.MenuHelper.choose_character(
                            character=self.players[i].character,
                            gamestate=self.gamestate,
                            controller=self.players[i].controller,
                            costume=i,
                            swag=False,
                            cpu_level=self.players[i].lvl,
                            start=False)  # HMN needed to start cpu-only game

            elif self.gamestate.menu_state is melee.Menu.STAGE_SELECT:
                melee.MenuHelper.choose_stage(
                    stage=stage,
                    gamestate=self.gamestate,
                    controller=self.players[self.menu_control_agent].controller)

            elif self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                if self.gamestate.frame < -83:
                    continue
                else:
                    return self.observation_space(self.gamestate)

            else:
                melee.MenuHelper.choose_versus_mode(self.gamestate, self.players[self.menu_control_agent].controller)


    def step(self):
        if self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            for i in range(len(self.players)):
                if self.players[i].agent_type == "AI":
                    # `action` is one of N possible actions an agent can take
                    #   as defined in action_space
                    controller_input = self.action_space(self.players[i].action)

                    # execute must be written to support any action from 
                    #   ActionSpace
                    controller_input.execute(self.players[i].controller)    

            self.gamestate = self.console.step()

            observation, reward, done, info = self.observation_space(self.gamestate)

            for i in range(len(self.players)):
                if self.players[i].defeated == True and len(observation) < len(self.players):
                    observation = np.insert(observation, i, np.full(observation.shape[1], -1), axis=0)

            return observation, reward, done, info
        else:
            return None, None, True, None

    def close(self):
        for t, c in self.controllers.items():
            c.disconnect()
        self.observation_space._reset()
        self.gamestate = None
        self.console.stop()
        time.sleep(2) 