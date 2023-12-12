import os
import subprocess

def construct_simple_game_name(rewards="dense", goal="detailed", seed=1234, log_path=False):
    """ Constructs game path"""
    file_name = f"r_{rewards}__g_{goal}__seed_{seed}.z8"
    game_path = os.path.join("games","tw_games","simple",file_name)
    
    if log_path:
        game_path = f"tw_games__simple__r_{rewards}__g_{goal}__seed_{seed}"
    
    return game_path


def construct_custom_game_name(world_size=2, objects=10, length=5, seed=1234, log_path=False):
    """ Constructs game path"""
    file_name = f"w_{world_size}__o_{objects}__l_{length}__seed_{seed}.z8"
    game_path = os.path.join("games","tw_games","custom",file_name)

    if log_path:
        game_path = f"tw_games__custom__w_{world_size}__o_{objects}__l_{length}__seed_{seed}"

    return game_path

def generate_simple_game(rewards="dense", goal="detailed", seed=1234):
    """ Generates simple game"""
    simple_game_path = construct_simple_game_name(rewards,goal,seed)
    subprocess.run(" ".join([
        "tw-make",
        "tw-simple",
        "--rewards",rewards, 
        "--goal",  goal, 
        "--seed",  seed, 
        "--output", simple_game_path
        ]), shell=True)


def generate_custom_game(world_size=2, objects=10, length=5, seed=1234):
    """ Generates custom game"""
    custom_game_path = construct_custom_game_name(world_size,objects,length,seed)
    subprocess.run(" ".join([
        "tw-make",
        "custom",
        "--world-size",world_size, 
        "--nb-objects",  objects,
        "--quest-length", length, 
        "--seed",  seed, 
        "--output", custom_game_path
        ]), shell=True)
