# LLamp - Large Languge Models for Planning

This is a package that uses LLMs (closed and open-source) for planning. 

**WARNING PACKAGE IS STILL UNDER DEVELOPMENT and requirements needs cleaning up.**

## Installation:
1. Textworld Game (pip install textworld)
2. Textworld Visualisation (pip install -r requirements_textworld_visualisation.txt)
3. (install chromedriver or firefox driver)

## Playgame:
The following is accepted:
```bash
python3 playgrounds/playground_tw_gym.py {human/openai/...} --custom/--simple {PARAMS}
```

e.g.:
```bash
python3 playgrounds/playground_tw_gym.py human --custom 1 2 2
```

**Or:**
1. (In terminal with browser visualiser) `tw-play tw_games/first_game.z8 --viewer`
2. (as Gym environement in terminal) `python3 playgrounds/playground_tw_gym.py`


## Generate New Textworld games using helper script
```bash
python3 generate_games.py --simple/--custom {PARAMS}
```

e.g.
```bash
python3 generate_games.py --custom 2 2 2 1234
```


## Generate New Textworld games using TW
1. `tw-make custom --world-size 2 --nb-objects 10 --quest-length 5 --seed 1234 --output games/tw_games/w2_o10_l5_game.z8`

2. `tw-make tw-simple --rewards dense --goal detailed --seed 1234 --output games/tw_games/simple/r_dense__g_detailed__seed_1234.z8`

Rewards: (dense, balanced, sparse)
Goal: (detailed, brief, none)

Reference: [https://textworld.readthedocs.io/en/stable/tw-make.html#types-of-game-to-create]



### Available Commands to agent:
```bash
Available commands:
  look:                describe the current room
  goal:                print the goal of this game
  inventory:           print player's inventory
  go <dir>:            move the player north, east, south or west
  examine ...:         examine something more closely
  eat ...:             eat edible food
  open ...:            open a door or a container
  close ...:           close a door or a container
  drop ...:            drop an object on the floor
  take ...:            take an object that is on the floor
  put ... on ...:      place an object on a supporter
  take ... from ...:   take an object from a container or a supporter
  insert ... into ...: place an object into a container
  lock ... with ...:   lock a door or a container with a key
  unlock ... with ...: unlock a door or a container with a key
```

