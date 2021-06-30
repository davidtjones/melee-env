# From MeleeEnv
    def reset(self):
        # currently not working under the current slippi spec. All commands while paused are ignored.
        while True:
            self.gamestate = self.console.step()
            if self.gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
                melee.MenuHelper.choose_character(
                    character=melee.enums.Character.FOX,
                    gamestate=self.gamestate,
                    controller=self.controllers['ai'],
                    costume=2,
                    swag=False,
                    start=False)

                melee.MenuHelper.choose_character(
                    character=melee.enums.Character.FOX,
                    gamestate=self.gamestate,
                    controller=self.controllers['cpu'],
                    cpu_level=1,
                    swag=False,
                    start=False)


            elif self.gamestate.menu_state is melee.Menu.STAGE_SELECT:
                melee.MenuHelper.choose_stage(stage=melee.enums.Stage.FINAL_DESTINATION,
                                              gamestate=self.gamestate,
                                              controller=self.controllers['ai'])

            elif self.gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                # in a game, need to press start!
                pressed_start = False 
                start_push_time = False

                while True:
                    self.gamestate = self.console.step()
                    self.controllers['ai'].release_all()
                    print(self.gamestate.frame)
                    if self.gamestate.frame > 0 and not pressed_start: # can pause game?
                        if not start_push_time:
                            start_push_time = time.time()  # when did we press start?
                            print(start_push_time)
                        self.controllers['ai'].press_button(melee.enums.Button.BUTTON_START)
                        print(pressed_start, start_push_time)
                        if start_push_time and time.time() > start_push_time + 1:  # wait 2 secs
                            self.controllers['ai'].release_all()
                            pressed_start = True  # start has been pressed
                            print("start pressed :)")

                    if self.gamestate.frame > 0 and pressed_start:  # time to press LRAS
                        self.controllers['ai'].press_shoulder(melee.enums.Button.BUTTON_L, 1)
                        self.controllers['ai'].press_shoulder(melee.enums.Button.BUTTON_R, 1)
                        self.controllers['ai'].press_button(melee.enums.Button.BUTTON_A)
                        self.controllers['ai'].press_button(melee.enums.Button.BUTTON_START)

                    if self.gamestate.menu_state not in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                        # SUCCESS!
                        print(self.gamestate.menu_state)        
                        
            else:
                melee.MenuHelper.choose_versus_mode(self.gamestate, self.controllers['ai'])
