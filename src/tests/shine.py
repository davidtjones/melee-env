from src.setup.project import Project
import melee
from melee import enums

p = Project()
p.set_ff(False)
p.use_vulkan()

# Setup console
print(str(p.slippi_bin))
console = melee.Console(
    path=str(p.slippi_bin),
    dolphin_home_path=str(p.home)+"/"
    )

# Setup controllers
controllers = [
    melee.Controller(console=console, port=1),
    melee.Controller(console=console, port=2)]

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
            melee.MenuHelper.choose_character(character=enums.Character.FOX,
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
        for i in range(len(controllers)):
            foxes.append(gamestate.player[i+1])  # players are 1-indexed
        
        data = zip(foxes, controllers)

        # multishine constantly
        for fox_state, controller in data:
            if fox_state.action in [enums.Action.STANDING]:
                controller.tilt_analog_unit(enums.Button.BUTTON_MAIN, 0, -1)

            if fox_state.action in [enums.Action.CROUCHING]:
                controller.release_button(enums.Button.BUTTON_Y)
                controller.press_button(enums.Button.BUTTON_B)

            if fox_state.action == enums.Action.KNEE_BEND:
                if fox_state.action_frame == 3:
                    controller.release_button(enums.Button.BUTTON_Y)
                    controller.press_button(enums.Button.BUTTON_B)

            if fox_state.action == enums.Action.DOWN_B_GROUND:
                controller.release_button(enums.Button.BUTTON_B)
                controller.press_button(enums.Button.BUTTON_Y)

            if fox_state.hitstun_frames_left > 0:
                controller.release_all()


    else:
        melee.MenuHelper.choose_versus_mode(gamestate, controllers[0])
