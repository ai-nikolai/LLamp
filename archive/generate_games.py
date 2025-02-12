import sys
from llamp import utils


__docstring = """
The way to use this function is:

```bash
python3 generate_games.py --simple {dense,balanced,sparse} {detailed, brief, none} [seed]
```

OR:

```bash
python3 generate_games.py --custom [world_size(num of rooms)] [objects] [quest_length] [seed]
```
"""

if __name__=="__main__":
    if sys.argv:
        pass
    else:
        print("No arguments passed")
        exit()
   

    game_type = sys.argv[1]
    if len(sys.argv)>2:
        params = sys.argv[2:]
    if game_type=="--simple":
        utils.generate_simple_game(*params)
    elif game_type=="--custom":
        utils.generate_custom_game(*params)