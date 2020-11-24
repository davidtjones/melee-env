from src.config.project import Project
import melee

p = Project()
p.set_ff(False)
p.use_vulkan()

# Setup console
print(str(p.slippi_bin))
console = melee.Console(path=str(p.slippi_bin))

# Setup controllers
controllers = [
    melee.Controller(console=console, port=1),
    melee.Controller(console=console, port=2),
    melee.Controller(console=console, port=3),
    melee.Controller(console=console, port=4)]

console.run(iso_path=p.iso)
console.connect()

for c in controllers: 
    c.connect()

# Do things
while True:

    gamestate = console.step()
    if gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
        # choose fox, press start
        for c in controllers:
            melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=c,
                                          swag=True,
                                          start=True)

    
    elif gamestate.menu_state is melee.Menu.STAGE_SELECT:
        melee.MenuHelper.choose_stage(melee.enums.Stage.FINAL_DESTINATION,
                                      gamestate,
                                     controllers[0])

    elif gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        foxes = []
        for i in range(4):
            foxes.append(gamestate.player[i+1])  # players are 1-indexed
        
        data = zip(foxes, controllers)

        # multishine constantly
        for fox_state, controller in data:
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
        melee.MenuHelper.choose_versus_mode(gamestate, controllers[0])
