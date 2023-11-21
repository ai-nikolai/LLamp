# LLamp - Large Languge Models for Planning

This is a package that uses LLMs (closed and open-source) for planning. 

**WARNING PACKAGE IS STILL UNDER DEVELOPMENT and requirements needs cleaning up.**

## Installation:
1. Textworld Game (pip install textworld)
2. Textworld Visualisation (pip install -r requirements_textworld_visualisation.txt)
3. (install chromedriver or firefox driver)


## Generate New Textworld games:
1. `tw-make custom --world-size 2 --nb-objects 10 --quest-length 5 --seed 1234 --output tw_games/w2_o10_l5_game.z8`

## Playgame:
1. (In terminal with browser visualiser) `tw-play tw_games/first_game.z8 --viewer`
2. (as Gym environement in terminal) `python3 playground_tw_gym.py`


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

