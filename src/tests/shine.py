from src.setup.dconfig import DolphinConfig
import melee
from melee import enums
import sys
import signal

# This script is a demonstration of libmelee and some of the tools built in this
#   project. You can play with the number of AI/CPUs/Human players and 
#   dolphin/libmelee will automatically configure for the right controller 
#   setup. Additionally, fast-forward and vulkan rendering can be toggled. For 
#   more example usage, see libmelee. 

# Choose "AI", "HMN", "CPU", or None.
players = ["AI", "AI", "AI", "AI"]

FAST_FORWARD = False
AI_STARTS_GAME = True

# Dolphin setup
d = DolphinConfig()
d.set_ff(FAST_FORWARD)
d.use_render_interface("vulkan")  # can also be "opengl"

# Setup console
console = melee.Console(
    path=str(d.slippi_bin_path),
    dolphin_home_path=str(d.home)+"/",
    blocking_input=False  # for long processing between states
    )

# This isn't necessary, but makes it so that Dolphin will get killed when you ^C
def signal_handler(sig, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Configure Dolphin for the correct controller setup, add controllers
controllers = []
for idx, player in enumerate(players):
    if player == "HMN":
        d.set_controller_type(idx+1, enums.ControllerType.GCN_ADAPTER)
        controllers.append(melee.Controller(console=console, port=idx+1, type=melee.ControllerType.GCN_ADAPTER))
    elif player in ["AI", "CPU"]:
        d.set_controller_type(idx+1, enums.ControllerType.STANDARD)
        controllers.append(melee.Controller(console=console, port=idx+1))
    else:  # no player
        d.set_controller_type(idx+1, enums.ControllerType.UNPLUGGED)

menu_control_agent_idx = players.index("AI") if "AI" in players else players.index("CPU")

console.run(iso_path=d.iso_path)
console.connect()

[c.connect() for c in controllers if c is not None]
non_hmn_controllers = {i: (players[i], controllers[i]) for i in range(len(controllers)) if players[i] in ["CPU", "AI"]}
ai_controllers = [controllers[i] for i in range(len(controllers)) if players[i] == "AI"]

# Game started, perform in-game actions.
while True:
    gamestate = console.step()
    if gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
        # choose fox, press start
        for i, (t, c) in non_hmn_controllers.items():
            if t == "AI":
                melee.MenuHelper.choose_character(
                    character=enums.Character.FOX,
                    gamestate=gamestate,
                    controller=c,
                    swag=True,
                    start=AI_STARTS_GAME)
            else:
                melee.MenuHelper.choose_character(
                    character=enums.Character.FOX,
                    gamestate=gamestate,
                    controller=c,
                    swag=False,
                    cpu_level=1,
                    start=False)  # HMN needed to start cpu-only game
     
    elif gamestate.menu_state is melee.Menu.STAGE_SELECT:
        melee.MenuHelper.choose_stage(
            melee.enums.Stage.FINAL_DESTINATION,
            gamestate,
            controllers[menu_control_agent_idx])

    elif gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        foxes = []
        for i, (t, c) in non_hmn_controllers.items():
            if t == 'AI':
                foxes.append(gamestate.players[i+1])  # players are 1-indexed
        
        data = zip(foxes, ai_controllers)

        # multishine constantly
        for fox_state, controller in data:
            melee.techskill(fox_state, controller)

    else:
        melee.MenuHelper.choose_versus_mode(gamestate, controllers[menu_control_agent_idx])
