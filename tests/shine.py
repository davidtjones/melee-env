import melee

# Setup console
console = melee.Console(path="squashfs-root/usr/bin/")

# Setup controllers
controller = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console,
                                    port=2,
                                    type=melee.enums.ControllerType.GCN_ADAPTER)

console.run()
console.connect()

controller.connect()
controller_human.connect()

# Do things
while True:

    gamestate = console.step()
    if gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
        # choose fox, press start
        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          port=1,
                                          controller=controller,
                                          swag=True)
        

    elif gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        fox_state = gamestate.player[1]
        player_state = gamestate.player[2]
        
        # multishine constantly
        if fox_state.action in [melee.enums.Action.STANDING]:
            controller.tilt_analog_unit(melee.enums.Button.BUTTON_MAIN, 0, -1)

        if fox_state.action in [melee.enums.Action.CROUCHING]:
            controller.release_button(melee.enums.Button.BUTTON_Y)
            controller.press_button(melee.enums.Button.BUTTON_B)

        if fox_state.action is melee.enums.Action.KNEE_BEND and fox_state.action_frame is 3:
            controller.release_button(melee.enums.Button.BUTTON_Y)
            controller.press_button(melee.enums.Button.BUTTON_B)

        if fox_state.action is melee.enums.Action.DOWN_B_GROUND:
            controller.release_button(melee.enums.Button.BUTTON_B)
            controller.press_button(melee.enums.Button.BUTTON_Y)

        if fox_state.hitstun_frames_left > 0:
            controller.release_all()


    else:
        melee.MenuHelper.choose_versus_mode(gamestate, controller)
