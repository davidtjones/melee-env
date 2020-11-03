import melee

# Setup console
console = melee.Console(path="squashfs-root/usr/bin/")

# Setup controllers
c1port=1
c2port=2
controller1 = melee.Controller(console=console, port=c1port)
controller2 = melee.Controller(console=console, port=c2port)

console.run()
console.connect()

controller1.connect()
controller2.connect()

# Do things
while True:

    gamestate = console.step()
    if gamestate.menu_state is melee.Menu.CHARACTER_SELECT:
        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controller1,
                                          costume=1,
                                          swag=True,
                                          start=True)

        melee.MenuHelper.choose_character(character=melee.enums.Character.FOX,
                                          gamestate=gamestate,
                                          controller=controller2,
                                          costume=2,
                                          swag=True)
        

    else:
        melee.MenuHelper.choose_versus_mode(gamestate, controller1)
