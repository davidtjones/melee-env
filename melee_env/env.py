from melee_env.dconfig import DolphinConfig
import melee
from melee import enums
import numpy as np
import sys
import time
import code

class MeleeEnv:
    def __init__(self, 
        iso_path,
        players,
        ai_starts_game=True,
        blocking_input=True,
        port=51441,
        fast_forward=False,
        mute_game=False,
        dsp_backend='Cubeb'

        ):

        self.d = DolphinConfig()
        self.d.set_ff(fast_forward)

        self.d.set_dsp_backend(dsp_backend)

        if mute_game:
            self.d.set_volume(0)
        else:
            self.d.set_volume(25)

        self.iso_path = iso_path
        self.players = players
        self.slippi_port=port
        self.fast_forward = fast_forward

        # inform other players of other players
        # for player in self.players:
        #     player.set_player_keys(len(self.players))
        
        if len(self.players) == 2:
            self.d.set_center_p2_hud(True)
        else:
            self.d.set_center_p2_hud(False)

        self.blocking_input = blocking_input
        self.ai_starts_game = ai_starts_game

        self.gamestate = None


    def start(self):
        if sys.platform == "linux":
            dolphin_home_path = str(self.d.slippi_home)+"/"
        elif sys.platform == "win32":
            dolphin_home_path = None

        self.console = melee.Console(
            path=str(self.d.slippi_bin_path),
            dolphin_home_path=dolphin_home_path,
            blocking_input=self.blocking_input,
            tmp_home_directory=True, 
            slippi_port=self.slippi_port)

        # print(self.console.dolphin_home_path)  # add to logging later
        # Configure Dolphin for the correct controller setup, add controllers
        human_detected = False

        for i in range(len(self.players)):
            curr_player = self.players[i]
            if curr_player.agent_type == 'HMN':
                self.d.set_controller_type(i+1, enums.ControllerType.GCN_ADAPTER)
                curr_player.controller = melee.Controller(console=self.console, port=i+1, type=melee.ControllerType.GCN_ADAPTER)
                curr_player.port = i+1
                human_detected = True
            elif curr_player.agent_type in ['AI', 'CPU']:
                self.d.set_controller_type(i+1, enums.ControllerType.STANDARD)
                curr_player.controller = melee.Controller(console=self.console, port=i+1)
                self.menu_control_agent = i
                curr_player.port = i+1 
            else:  # no player
                self.d.set_controller_type(i+1, enums.ControllerType.UNPLUGGED)
            
        if self.ai_starts_game and not human_detected:
            self.ai_press_start = True

        else:
            self.ai_press_start = False  # don't let ai press start without the human player joining in. 

        if self.ai_starts_game and self.ai_press_start:
            self.players[self.menu_control_agent].press_start = True

        self.console.run(iso_path=self.iso_path)
        self.console.connect()

        [player.controller.connect() for player in self.players if player is not None]

        self.gamestate = self.console.step()

    def _force_release(self):
        # ensure that agents don't act up during menu operations
        for i in range(len(self.players)):
            if self.players[i].agent_type == 'AI' and i != self.menu_control_agent:
                self.players[i].controller.release_all()

    def setup(self, stage):
        for player in self.players:
            player.defeated = False
        
        while True:
            self.gamestate = self.console.step()
            
            if self.gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
                for i in range(len(self.players)):
                    if self.players[i].agent_type == 'AI':
                        melee.MenuHelper.choose_character(
                            character=self.players[i].character,
                            gamestate=self.gamestate,
                            controller=self.players[i].controller,
                            swag=False,
                            start=self.players[i].press_start)

                    if self.players[i].agent_type == 'CPU':
                        melee.MenuHelper.choose_character(
                            character=self.players[i].character,
                            gamestate=self.gamestate,
                            controller=self.players[i].controller,
                            swag=False,
                            cpu_level=self.players[i].lvl,
                            start=self.players[i].press_start)  

            elif self.gamestate.menu_state is melee.Menu.STAGE_SELECT:
                self._force_release()
                melee.MenuHelper.choose_stage(
                    stage=stage,
                    gamestate=self.gamestate,
                    controller=self.players[self.menu_control_agent].controller)

            elif self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                return self.gamestate, False  # game is not done on start
                
            else:
                self._force_release()
                melee.MenuHelper.choose_versus_mode(self.gamestate, self.players[self.menu_control_agent].controller)

    def step(self):
        stocks = np.array([self.gamestate.players[i].stock for i in list(self.gamestate.players.keys())])
        done = not np.sum(stocks[np.argsort(stocks)][::-1][1:])

        if self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            self.gamestate = self.console.step()
        return self.gamestate, done


    def close(self):
        for t, c in self.controllers.items():
            c.disconnect()
        self.observation_space._reset()
        self.gamestate = None
        self.console.stop()
        time.sleep(2) 