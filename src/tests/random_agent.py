from src.config.project import Project
from src.ai.tools.action_space import ActionSpace, ControlState
import melee

p = Project()

# Setup Console
console = melee.Console(path=str(p.slippi_bin))

# Setup Controllers
controller_ai = melee.Controller(console=console, port=1)
controller_cpu = melee.Controller(console=console, port=2)

console.run(iso_path=p.iso)
console.connect()

controller_ai.connect()
controller_cpu.connect()

# Get the actions available to our agent
asp = ActionSpace()

input("Press Enter to start the magic!")

while True:

    gamestate = console.step()
    if gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controller_ai,
                                          swag=True,
                                          start=True)

        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controller_cpu,
                                          cpu_level=1,
                                          costume=3,
                                          swag=False,
                                          start=False)

    elif gamestate.menu_state is melee.Menu.STAGE_SELECT:
        melee.MenuHelper.choose_stage(stage=melee.enums.Stage.FINAL_DESTINATION,
                                      gamestate=gamestate,
                                      controller=controller_ai)

    elif gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        # choose random actions
        action = asp.generate_random_control_state()
        action.execute(controller_ai)
        pass

    else:
        melee.MenuHelper.choose_versus_mode(gamestate, controller_ai)
