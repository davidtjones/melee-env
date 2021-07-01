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

# From action space (define the real controller space)
self.button_space = np.array([0.0, 1.0])
self.shoulder_space = np.array([0.0,          # none
                                # 0.1,         # light press
                                1.0])         # hard press    

self.c_stick_space = np.array([[0.0, 0.0],    # center
                               [1.0, 0.0],    # right
                               [0.0, -1.0],   # down
                               [-1.0, 0.0],   # left
                               [0.0, 1.0]])   # up

# The main control stick is slightly harder as there isn't a simple
#   square stick box, so some calculation is needed to find legal 
#   values. Also of note, the space of values of the stick needs to
#   include no-op, so an odd value must be used on the number of 
#   steps. 
self.stick_values = np.linspace(-1, 1, (2**3)-1)

# create tuples of all possible stick values:
self.stick_space_square = np.array(
    np.meshgrid(self.stick_values, self.stick_values)).T.reshape(-1, 2)

# These contain illegal values in a circular stick box, you can never
#   achieve (1,1), for example. For any values a and b,  a^2 + b^2 > 1 
#   are thus illegal. 
dist = np.sqrt(
    self.stick_space_square[:, 0]**2 + self.stick_space_square[:, 1]**2)
legal_indices = np.where(dist <= 1)

self.stick_space_circle = self.stick_space_square[legal_indices]