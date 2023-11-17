# LLamp

## Installation:
1. Textworld Game (pip install textworld)
2. Textworld Visualisation (pip install -r requirements_textworld_visualisation.txt)
3. (install chromedriver or firefox driver)


## Generate New Textworld games:
1. `tw-make custom --world-size 2 --nb-objects 10 --quest-length 5 --seed 1234 --output tw_games/w2_o10_l5_game.z8`

## Playgame:
1. (In terminal with browser visualiser) `tw-play tw_games/first_game.z8 --viewer`
2. (as Gym environement in terminal) `python3 playground_tw_gym.py`
