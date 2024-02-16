import os
import subprocess

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

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


def openai_model(model="gpt-3.5-turbo-0125"):
    """OpenAI Closure"""
    import openai
    client = openai.OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
        # api_key=OPENAI_KEY,
    )
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_openai(prompt, system_prompt=None):
        """Call OpenAI API in a simple way. (System Prompt is skipped for now.)"""
        openai_prompt = [{
            "role": "user", 
            "content": prompt
        }]

        chat_completion = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            # model="gpt-3.5-turbo-0125",
            # model="gpt-4-turbo-preview",
            model=model,
            messages=openai_prompt,
            temperature=0.8
        )
        chat_message = chat_completion.choices[0].message.content
        return chat_message

    return call_openai


def cohere_model():
    """Cohere Closure"""
    import cohere
    API_KEY = os.environ['COHERE_API_KEY']

    co = cohere.Client(API_KEY)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
    def call_cohere(prompt, system_prompt=None):
        """Call OpenAI API in a simple way. (System Prompt is skipped for now.)"""

        response = co.chat(
            prompt,
            model="command",
            # chat_history=chat_history,
            temperature=0.8
        )

        answer = response.text
        return answer

    return call_cohere


