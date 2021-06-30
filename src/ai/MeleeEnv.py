import time
from src.setup.dconfig import DolphinConfig
import numpy as np
import melee
from melee import enums
import code
import time
    
class MeleeEnv:
    def __init__(self, 
        players,
        action_space,
        observation_space,
        fast_forward=False, 
        blocking_input=False,
        ai_starts_game=False):

        self.d = DolphinConfig()
        self.d.set_ff(fast_forward)

        self.players = players

        self.action_space = action_space 
        self.observation_space = observation_space

        self.blocking_input = blocking_input
        self.ai_starts_game = ai_starts_game
        
        self.gamestate = None


    def start(self):
        self.console = melee.Console(
            path=str(self.d.slippi_bin),
            dolphin_home_path=str(self.d.home),
            blocking_input=self.blocking_input)  # broken in 0.21.0

        # Configure Dolphin for the correct controller setup, add controllers
        self.controllers = []
        for idx, player in enumerate(players):
            if player == "HMN":
                d.set_controller_type(idx+1, enums.ControllerType.GCN_ADAPTER)
                self.controllers.append(melee.Controller(console=console, port=idx+1, type=melee.ControllerType.GCN_ADAPTER))
            elif player in ["AI", "CPU"]:
                d.set_controller_type(idx+1, enums.ControllerType.STANDARD)
                self.controllers.append(melee.Controller(console=console, port=idx+1))
            else:  # no player
                d.set_controller_type(idx+1, enums.ControllerType.UNPLUGGED)
        
        self.menu_control_agent = self.players.index("AI") if "AI" in players else players.index("CPU")
        self.console.run(iso_path=self.project.iso)
        self.console.connect()

        [c.connect() for c in controllers if c is not None]
        self.non_hmn_controllers = {i: (players[i], controllers[i]) for i in range(len(controllers)) if players[i] in ["CPU", "AI"]}
        self.ai_controllers = [controllers[i] for i in range(len(controllers)) if players[i] == "AI"]

        self.gamestate = self.console.step()
 
    def setup(self):
        while True:
            self.gamestate = self.console.step()
            if self.gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
                for i, (t, c) in non_hmn_controllers.items():
                    if t == "AI":
                        melee.MenuHelper.choose_character(
                            character=melee.enums.Character.FOX,
                            gamestate=self.gamestate,
                            controller=c,
                            costume=i,
                            swag=False,
                            start=self.ai_starts_game)
                    else:
                        melee.MenuHelper.choose_character(
                            character=enums.Character.FOX,
                            gamestate=self.gamestate,
                            controller=c,
                            costume=i,
                            swag=False,
                            cpu_level=1,
                            start=False)  # HMN needed to start cpu-only game

            elif self.gamestate.menu_state is melee.Menu.STAGE_SELECT:
                melee.MenuHelper.choose_stage(
                    stage=melee.enums.Stage.FINAL_DESTINATION,
                    gamestate=self.gamestate,
                    controller=self.ai_controllers[0])

            elif self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                if self.gamestate.frame < -83:
                    continue
                else:
                    return self.observation_space(self.gamestate)

            else:
                melee.MenuHelper.choose_versus_mode(self.gamestate, self.controllers['ai'])


    def step(self, action=None):
        if self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
           
            if action:
                controller_input = self.action_space(action)
                controller_input.execute(self.controllers['ai'])    

            self.gamestate = self.console.step()

            return self.observation_space(self.gamestate)
        else:
            return None, None, True, None

    def close(self):
        for t, c in self.controllers.items():
            c.disconnect()
        self.observation_space._reset()
        self.gamestate = None
        self.console.stop()
        time.sleep(2) 