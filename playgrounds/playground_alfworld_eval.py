import yaml
import csv
import os
import json
import re
import argparse
from datetime import datetime


import alfworld
import alfworld.agents.environment

import cohere


from llamp.llms.human import Human
from llamp.llms.api import (
    AnthropicChat, AnthropicText,
    CohereChat, CohereChatText, CohereText,
    OpenAIChat, OpenAIChatText, OpenAIText, OpenAIChatTextSampling
)


from playground_alfworld_ablation_generator import generate_string_prompt, remove_keys
from playground_alfworld_react_prompt_utils import return_react_examples, return_agentbench_prompts, return_json_react_examples


from prompts.alfworld_prompts_utils_v4_clean_base import clean_v4_base_0, clean_v4_base_1, clean_v4_base_2
from prompts.alfworld_prompts_utils_v4_cool_base import cool_v4_base_0, cool_v4_base_1, cool_v4_base_2
from prompts.alfworld_prompts_utils_v4_examine_base import examine_v4_base_0, examine_v4_base_1, examine_v4_base_2
from prompts.alfworld_prompts_utils_v4_heat_base import heat_v4_base_0, heat_v4_base_1, heat_v4_base_2
from prompts.alfworld_prompts_utils_v4_put_base import put_v4_base_0, put_v4_base_1, put_v4_base_2
from prompts.alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base_0, puttwo_v4_base_1, puttwo_v4_base_2


# Git patch commit: https://stackoverflow.com/questions/1085162/commit-only-part-of-a-files-changes-in-git
#################################################################
#GAME LOOP & ENV Related
#################################################################

ENV_TYPES = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
} 

ENV_TO_EXAMPLE_MAPPING_0 = {
    "clean" : clean_v4_base_0,
    "cool"  : cool_v4_base_0,
    "examine"   : examine_v4_base_0,
    "heat"  : heat_v4_base_0,
    "put"   : put_v4_base_0,
    "puttwo"    : puttwo_v4_base_0
}

ENV_TO_EXAMPLE_MAPPING_1 = {
    "clean" : clean_v4_base_1,
    "cool"  : cool_v4_base_1,
    "examine"   : examine_v4_base_1,
    "heat"  : heat_v4_base_1,
    "put"   : put_v4_base_1,
    "puttwo"    : puttwo_v4_base_1
}

ENV_TO_EXAMPLE_MAPPING_2 = {
    "clean" : clean_v4_base_2,
    "cool"  : cool_v4_base_2,
    "examine"   : examine_v4_base_2,
    "heat"  : heat_v4_base_2,
    "put"   : put_v4_base_2,
    "puttwo"    : puttwo_v4_base_2
}


def get_env_type(env_name):
    """ Extracts which type of env it is"""
    env_type = ""
    for key, value in ENV_TYPES.items():
        if env_name.startswith(key):
            env_type = value
    return env_type


def process_action(action, track_is_illegal=False):
    """Processes Action of Agent."""
    illegal_action = False

    if 'action("' in action:
        actions = action.split('action("')
        action = actions[1].split('")')[0]
        print(f"Extracted Action:{action}")

    elif ('"action" : "' in action):
        actions = action.split('"action" : "')
        action = actions[1].split('"')[0]
        print(f"Extracted Action:{action}")

    elif ('"action": "' in action):
        actions = action.split('"action": "')
        action = actions[1].split('"')[0]
        print(f"Extracted Action:{action}")

    elif ('"action":"' in action):
        actions = action.split('"action":"')
        action = actions[1].split('"')[0]
        print(f"Extracted Action:{action}")

    #TODO: this is for AGENTBENCH, need to refactor.
    elif "ACTION:" in action:
        actions = action.split('ACTION:')
        action = actions[1]
        print(f"Extracted Action:{action}")

    else:
        illegal_action = True

    if track_is_illegal:
        return action, illegal_action
    else:
        return action



def process_ob(ob, track_nothing_happens=False):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ')+2:]
    
    nothing_happens = False

    if ob == "Nothing happens.":
        nothing_happens = True
        # ob = "Invalid or Impossible Action. Try again." 

    if not ob.endswith("\n"):
        ob += "\n"

    if track_nothing_happens:
        return ob, nothing_happens
    else:
        return ob


def transform_put_action(action):
    """ Put action grammar correction. """
    put_regex_1 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\son(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    put_regex_2 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\sin(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""

    if action.startswith("put"):
        answer = re.match(put_regex_1,action)
        if answer:
            action = action.replace(" on "," in/on ")

        else:
            answer = re.match(put_regex_2,action)
            if answer:
                action = action.replace(" in "," in/on ")
    return action





#################################################################
#PROMPT RELATED
#################################################################

OPENING_MARK="<<<"
OPENING_MARK=""
CLOSING_MARK=">>>"
CLOSING_MARK=""

HINTS=f"""
A few hints:
{OPENING_MARK}
1. When "Nothing happens." this means your action was not successful or not valid. If this happen, then try a valid action that you have not tried before.

2. If you repeat yourself, try a different valid action. 

3. Visit new places to find an object.

4. Some actions can be only executed in specific places, such as cleaning, heating, cooling...

5. Be literatal.

6. Initially you have not visited any places and you are starting at the 'starting_location'.

7. Generate one JSON output only.
{CLOSING_MARK}
"""

HINTS=""

INSTRUCTIONS=f"""
This is the list of all valid actions that you can use:
{OPENING_MARK}
- go to <dir> [example: go to table 1]
- open <obj> [example: open door 1]
- close <obj> [example: close door 1]
- put <obj> in/on <obj> [example: put apple 1 in/on table 1]
- take <obj> from <obj> [example: take apple 1 from table 1]
- cool <obj> with <obj> [example: cool apple 1 with fridge 1]
- heat <obj> with <obj> [example: heat apple 1 with fire 1]
- use <obj> [example: use desklamp 1]
{CLOSING_MARK}
"""

INSTRUCTIONS=""


BASE_PROMPT1 = "Interact with a household to solve a task."
BASE_PROMPT2 = "You will interact with the environment to solve the given task."

def generate_prompt_from_example(examples, return_raw_prompt = False, number_of_examples=1, base_prompt = "", instructions = "", hints = ""):
    """ Generates prompt """
    if number_of_examples >1:
        s_string="s"
        is_are = "are"
    else:
        s_string=""
        is_are = "is"
    number_of_examples_string = str(number_of_examples)

    #in case no alternative base_prompt is provided.
    if not base_prompt:
        base_prompt = BASE_PROMPT1

    #in case no alternative instructions is provided.
    if not instructions:
        instructions = INSTRUCTIONS

    #in case no alternative hints is provided.
    if not hints:
        hints = HINTS

    #########################################
    #
    #This is the part for the raw prompt.
    #
    #########################################
    raw_prompt = f"""
{base_prompt}
{instructions}

Here {is_are} {number_of_examples_string} example{s_string}:
{OPENING_MARK}
{examples}
{CLOSING_MARK}

{hints}
"""
    prompt = [{
                "role" : "system",
                "content" : raw_prompt
            }]

    if return_raw_prompt:
        return raw_prompt
    else:
        return prompt

# HINT1="""1. When "Nothing happens." this means your action was not successful or not valid. This can have a variety of reasons, such as not wrong format of the output, or doing something in the wrong location, or using objects that are not available.
# If this happen, then try a valid action that you have not tried before.

# 2. If you repeat yourself, try a different valid action. Re-evaluate your assumptions.

# 3. Visit new places to find an object.

# 4. Some actions can be only executed in specific places, such as cleaning, heating, cooling...

# 5. Generate just one JSON output.
# """






#################################################################
#Logging Related
#################################################################
def write_line_to_main_log_csv(name, data):
    """Writes one line of output into the main CSV"""
    with open(name, 'a', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if type(data) == list:
            wr.writerow(data)
        elif type(data) == dict:
            data_list = [x for _,x in data.items()]
            wr.writerow(data_list)
  
def save_prompt_file(file_path, raw_prompt):
    """ Saves a prompt file """
    with open(file_path, "w") as file:
        file.write(raw_prompt)


def get_empty_dict_from_csv_header(header):
    """Generate empty dict from csv header"""
    out_dict = {}
    for column_name in header:
        out_dict[column_name] = ""
    return out_dict







#################################################################
#AGENT Related
#################################################################
# TODO: REFACTOR
AGENT_MODEL_MAPPING = {
    "AnthropicChat" : ["claude-2.1", "claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
    "CohereChat" : ["command","command-nightly", "command-r", "command-r-plus"],
    "OpenAIChat" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106"],
    "AnthropicText" : ["claude-2.1", "claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
    "CohereText" : ["command","command-nightly", "command-r", "command-r-plus"],
    "OpenAIText" : ["davinci-002", "gpt-3.5-turbo-instruct"],
    "CohereChatText" : ["command","command-nightly", "command-r", "command-r-plus"],
    "OpenAIChatText" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106"],
    "OpenAIChatTextSampling" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview","gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106"]
}

            
def get_agent_and_model(llm_type, temperature=0.0, proposed_model=""):
    """ Returns Agent, Model"""
    print(llm_type)
    print(proposed_model)
    #Standard CHAT Models
    if llm_type == "AnthropicChat":
        model = "claude-2.1"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = AnthropicChat(temperature=temperature, model=model) 

    elif llm_type == "CohereChat":
        # model = "command"
        # model = "command-nightly"
        model = "command-r"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereChat(temperature=temperature, model=model)

    elif llm_type=="OpenAIChat":
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAIChat(temperature=temperature, model=model)
 


    #TEXT BASED MODELs
    elif llm_type =="AnthropicText":
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        # model = "claude-1.2"
        model = "claude-2.1"
        agent = AnthropicText(temperature=temperature, model=model) 

    elif llm_type=="CohereText":
        # model = "command"
        # model = "command-nightly"
        model = "command-r"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereText(temperature=temperature, model=model)

    elif llm_type=="OpenAIText":
        model = "davinci-002"
        model = "gpt-3.5-turbo-instruct"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAIText(temperature=temperature, model=model)     



    #CHAT MODELS used as TEXT MODELs
    elif llm_type=="CohereChatText":
        # model = "command"
        # model = "command-nightly"
        model = "command-r"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereChatText(temperature=temperature, model=model)


    elif llm_type=="OpenAIChatText":
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAIChatText(temperature=temperature, model=model) 


    elif llm_type=="OpenAIChatTextSampling":
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[llm_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAIChatTextSampling(temperature=temperature, model=model, temperature_jump=0.2) 


    elif llm_type=="Human":
        model = "Human"
        agent = HumanAgent()

    return agent, model



#################################################################
#Display Settings
#################################################################
def get_settings_string(react_prompt, agentbench_prompt, json_react_prompt, agent_type, llm_type, model, temperature, num_envs, starting_env, current_trial_name, keys_to_remove, num_examples, version, swap_order, keys_to_remove_string, correction):
    """ Creates a string to print to the user the current settings. """
    not_ours = react_prompt or agentbench_prompt or json_react_prompt
    if not_ours:
        if react_prompt:
            which_prompt = "ReAct"
        elif agentbench_prompt:
            which_prompt = "Agentbench"
        elif json_react_prompt:
            which_prompt = "JsonReAct"

    else:
        which_prompt = "Ours"

    display_text = ""
    display_text += f"You are going to run Alfworld Environment with the following settings:\n"
    display_text += f"   -Agent Type: {agent_type}\n"
    display_text += f"   -Agent Type: {which_prompt}\n"
    display_text += f"   -LLM Type: {llm_type}\n"
    display_text += f"   -Model: {model}\n"
    display_text += f"   -Temperature: {temperature}\n"
    display_text += f"   -Starting env: {starting_env}\n"
    display_text += f"   -Ending env: {starting_env+num_envs-1}\n"
    display_text += f"   -Num of envs: {num_envs}\n"
    display_text += f"   -Current Trial Name: {current_trial_name}\n"
    
    if not not_ours:
        display_text += f"   -Keys that will be removed: {keys_to_remove}\n"
        display_text += f"   -Number of our Prompts: {num_examples}\n"  
    if react_prompt:
        display_text += f"   -Number of React Examples: {num_examples}\n"  
    if agentbench_prompt:
        display_text += f"   -Prompt Version AgentBench: {version}\n"  
    if json_react_prompt:
        display_text += f"   -Number JsonReAct Examples: {num_examples}\n" 
    
    # Swap Order
    display_text += f"   -Swap Order of Prompts: {swap_order}\n" 

    #Name of prompt
    display_text += f"   -The prompt will be called: {keys_to_remove_string}\n" 

    #Name of prompt
    display_text += f"   -Correction will happen: {correction}\n" 


    display_text += "Do you want to continue? Press 'y' to continue."

    return display_text





#################################################################
#Env Prompt Logic
#################################################################
def get_prompt_example(react_prompt, agentbench_prompt, jsonreact_prompt, swap_order, num_examples, version, env_type, log_full_prompt=False, generate_example=True, keys_to_remove=[]):
    """ Get name of prompt and example prompts"""
    # Generate correct prompt for this environment (basically pick the right example).  
    new_base_prompt = ""
    swap_string = "-swaped" if swap_order else ""

    #REACT PROMPT or OUR PROMPT
    if react_prompt:
        num_examples = num_examples
        if generate_example:
            prompt_example = return_react_examples(env_type, num=num_examples, swap=swap_order)
        keys_to_remove_string = f"react-{num_examples}"+swap_string

    elif agentbench_prompt:
        num_examples = 1
        version = version
        if generate_example:
            prompt_example, new_base_prompt = return_agentbench_prompts(env_type, return_base=True, version=version)
        keys_to_remove_string = f"agentbench-v{version}"
        
    elif jsonreact_prompt:            
        num_examples = num_examples
        if generate_example:
            prompt_example = return_json_react_examples(env_type, num=num_examples)
        keys_to_remove_string = f"jsonreact-{num_examples}"

    else: #OURS
        num_examples = num_examples
        
        if generate_example:
            if swap_order:
                first_prompt_map = ENV_TO_EXAMPLE_MAPPING_2
                second_prompt_map = ENV_TO_EXAMPLE_MAPPING_1
            else: #the normal case.
                first_prompt_map = ENV_TO_EXAMPLE_MAPPING_1
                second_prompt_map = ENV_TO_EXAMPLE_MAPPING_2
            base_prompt = remove_keys(first_prompt_map[env_type], keys=keys_to_remove)
            prompt_example = generate_string_prompt(base_prompt)
            
            if num_examples==2:
                base_prompt = remove_keys(second_prompt_map[env_type], keys=keys_to_remove)
                prompt_example2 = generate_string_prompt(base_prompt)
                prompt_example += "\n\n"+prompt_example2

        if log_full_prompt:
            keys_to_remove_string = "+".join(keys_to_remove)+swap_string
 
        else:
            long_string = "short" if len(keys_to_remove) > 2 else "long"
            keys_to_remove_string = long_string+f"-{num_examples}"+swap_string

    if generate_example:
        return keys_to_remove_string, prompt_example, new_base_prompt, num_examples
    else:
        return keys_to_remove_string



# AGENT_MODEL_MAPPING = [
#     "AnthropicChat",
#     "CohereChat" ,
#     "OpenAIChat" ,
#     "AnthropicText" ,
#     "CohereText" ,
#     "OpenAIText" ,
#     "CohereChatText", 
#     "OpenAIChatText" ,
#     "OpenAIChatTextSampling" 
# ]


#################################################################
#Arg parse
#################################################################
def build_arg_parser():
    """ Returns the argument parser"""
    parser = argparse.ArgumentParser(description="Alfworld Env with various agents")
    parser.add_argument(
        "--agent",
        type=str,
        default="ours",
        choices=[
            "react",
            "react-replace",
            "jsonreact",
            "agentbench",
            "ours",
            "ours-text",
            "ours-replace"
        ],
        help="The Agent / Method choice.",
    )

    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-0125", help="Underlying Model to use.(Needs to align with agent, otherwise default model will be used.)")
    parser.add_argument(
        "--llm_type",
        type=str,
        default="OpenAIChatText",
        choices=[
            "AnthropicChat",
            "CohereChat" ,
            "OpenAIChat" ,
            "AnthropicText" ,
            "CohereText" ,
            "OpenAIText" ,
            "CohereChatText", 
            "OpenAIChatText" ,
            "OpenAIChatTextSampling" 
        ],
        help="The type of llamp.llms to use.",
    )

    parser.add_argument("--agent_version", type=int, default=1, help="Method Version (if applicable)")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature")
    parser.add_argument("--num_prompts", type=int, default=2, help="Number of prompts to use (if applicable) (LEGACY)")

    parser.add_argument("--prompt_indices", nargs='+', type=int, default=[1,0], help="A list of prompt indices to use, e.g. --prompt_indices 0 1")

    # Keys for our method
    parser.add_argument("--keys_to_remove", type=str, default="[]",help="Needs to be json.loads-able list of keys to remove (LEGACY).")
    parser.add_argument("--keys_to_use", type=str, help="Needs to be json.loads-able list of keys to use")
    parser.add_argument("--keys_renaming", type=str, help="Needs to be json.loads-able list of new key names.")

    # RUN / ENV:
    parser.add_argument("--trial_name", type=str, default="v3_0_eval_test", help="Underlying Model to use.(Needs to align with agent, otherwise default model will be used.)")
    parser.add_argument("--start_index", type=int, default=0, help="Starting Index to use (inclusive).")
    parser.add_argument("--end_index", type=int, default=0, help="Ending index to use (inclusive). (Overrides num_envs)")
    parser.add_argument("--num_envs", type=int,  default=1, help="Sets the num of envs to run (gets overriden by end index)")


    parser.add_argument(
        "--eval_split",
        type=str,
        default="eval_out_of_distribution",
        choices=[
            "eval_out_of_distribution",
            "eval_in_distribution"
            "jsonreact",
            "agentbench",
            "ours",
            "ours-text",
            "ours-replace"
        ],
        help="The alfworld split to use.",
    )
    parser.add_argument("--apply_correction", action="store_true", default=False, help="Whether to apply the 'Put Regex' correction")
    
    parser.add_argument("--force_run", action="store_true", default=False, help="Whether to apply the 'Put Regex' correction")

    return parser







#################################################################
#################################################################
#MAIN LOOP
#################################################################
#################################################################

if __name__=="__main__":

    # More things to track:
    # 1. Tokens generated / consumed (i.e. estimated price)
    # 2. Time taken 

    
    ####################################################
    # BASIC CONFIGURATION
    ####################################################
    BASE_FOLDER = "game_logs"
    BASE_EVAL_NAME = "alfworld_eval"
    MAIN_CSV_FILE_NAME = "alfworld_results"

    TEST_ENV = False
    # TEST_ENV = True


    parser = build_arg_parser()
    args = parser.parse_args()


    #CHANGE THIS ONE
    if not TEST_ENV:
        CURRENT_TRIAL_NAME = args.trial_name
    else:
        CURRENT_TRIAL_NAME = "v3_0_eval_test"

    ###############################
# TODO:
# 1. Make end start env as option as well (not only num of envs)
# 2. Make restart from last unfinished possible
# 3. Todo (record prompts more properly [based on order of input prompts])
    # Basic Init
    if not TEST_ENV:
        start_env_idx=args.start_index
        num_envs = args.num_envs
    else:
        start_env_idx=0
        num_envs = 1

    llm_type = args.llm_type
    # llm_type = "OpenAIChatTextSampling"
    # llm_type = "Human"
    model = args.model
    # model = "gpt-3.5-turbo-0301" #Adaplanner paper GPT3.5 (released when?)
    # model = "gpt-3.5-turbo-0613" #slightly newer version than 0301 (released 13.06.2023)
    # model = "gpt-3.5-turbo-1106" #sligthly newer version than 0613 (released 11.06.2023)
# gpt-3.5-turbo-instruct
# gpt-3.5-turbo-instruct-0914    
    temperature = args.temperature

    ###############################
    # Which METHOD to run (REACT, AGENTBENCH, OURS)
    agent_type = args.agent

    REACT_PROMPT = True if agent_type == "react" else False
    AGENTBENCH_PROMPT = True if agent_type == "agentbench" else False
    JSON_REACT_PROMPT = True if agent_type == "jsonreact" else False

    NOT_JSON_PROMPTS = REACT_PROMPT or AGENTBENCH_PROMPT or llm_type == "Human"
    
    NUM_EXAMPLES = args.num_prompts
    VERSION = args.agent_version

    CORRECTION = args.apply_correction

    # LEGACY
    SWAP_ORDER = True
    LOG_FULL_PROMPT = True


    ##############################
    # This applies to our prompts

    keys_to_remove = json.loads(args.keys_to_remove)

    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     # "places_visited", 
    #     # "current_inventory", 
    #     # "current_location", 
    #     # "current_objective",
    #     # "thought",
    #     # "action"
    # ]

    # #short with thought (naturally without current_objective)
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     "places_visited", 
    #     "current_inventory", 
    #     "current_location", 
    #     "current_objective",
    #     # "thought",
    #     # "action"
    # ]

    # #Long with thought
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     # "places_visited", 
    #     # "current_inventory", 
    #     # "current_location", 
    #     # "current_objective",
    #     # "thought",
    #     # "action"
    # ]


    # #short without thought with current_objective [i.e. "do we need full thoughts"]
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     "places_visited", 
    #     "current_inventory", 
    #     "current_location", 
    #     # "current_objective",
    #     "thought",
    #     # "action"
    # ]

    # #Long with thought without current_objective [i.e. "do we need full thoughts"]
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     # "places_visited", 
    #     # "current_inventory", 
    #     # "current_location", 
    #     "current_objective",
    #     # "thought",
    #     # "action"
    # ]

    # #thought + goal (react-2-goal) (i.e. what is better plan or thought) [need a few more of short without thought, long without thought and thought / plan swapped places]
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     "plan", 
    #     "places_visited", 
    #     "current_inventory", 
    #     "current_location", 
    #     "current_objective",
    #     # "thought",
    #     # "action"
    # ]


    # "long" no plan, + thought, no current_objective (i.e. just goal + current_obj + act)
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     "plan", 
    #     # "places_visited", 
    #     # "current_inventory", 
    #     # "current_location", 
    #     "current_objective",
    #     # "thought",
    #     # "action"
    # ]

    # "short" no plan, no thought (i.e. just goal + current_obj + act)
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     "plan", 
    #     "places_visited", 
    #     "current_inventory", 
    #     "current_location", 
    #     # "current_objective",
    #     "thought",
    #     # "action"
    # ]

    # #old "long"
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     # "places_visited", 
    #     # "current_inventory", 
    #     # "current_location", 
    #     # "current_objective",
    #     "thought",
    #     # "action"
    # ]

    # #old "short"
    # keys_to_remove = [
    #     "prompt",
    #     # "goal", 
    #     # "plan", 
    #     "places_visited", 
    #     "current_inventory", 
    #     "current_location", 
    #     "current_objective",
    #     "thought",
    #     # "action"
    # ]

    keys_to_remove_string2 = get_prompt_example(
        react_prompt=REACT_PROMPT,
        agentbench_prompt=AGENTBENCH_PROMPT, 
        jsonreact_prompt=JSON_REACT_PROMPT, 
        swap_order=SWAP_ORDER, 
        num_examples = NUM_EXAMPLES,
        version = VERSION,
        env_type="",
        log_full_prompt = LOG_FULL_PROMPT,
        generate_example=False,
        keys_to_remove=keys_to_remove)

    ##############################
    # Checking settings with the user. User needs to type y.
    keys_to_remove_string = "+".join(keys_to_remove)
    settings_string = get_settings_string(
            react_prompt = REACT_PROMPT, 
            agentbench_prompt = AGENTBENCH_PROMPT,
            json_react_prompt = JSON_REACT_PROMPT,
            agent_type = agent_type, 
            llm_type = llm_type, 
            model = model, 
            temperature = temperature, 
            num_envs = num_envs, 
            starting_env = start_env_idx, 
            current_trial_name = CURRENT_TRIAL_NAME, 
            keys_to_remove=keys_to_remove_string,
            num_examples = NUM_EXAMPLES,
            version = VERSION,
            swap_order = SWAP_ORDER,
            keys_to_remove_string = keys_to_remove_string2,
            correction = CORRECTION
        )

    print(settings_string)
    if args.force_run:
        print("WARNING: Running Anyways")
    else:
        user_input = input(">")
        if not (user_input=="y"):
            print("Exiting Programme, please change the settings in: playgrounds/playground_alfworld_eval.py")
            exit(1)


    #TODO for the future
    additional_prompt_annotation = ""


    ####################################################
    # OTHER IN-BUILT CONFIG
    ####################################################
    CREATE_NEW_LOG_CSV=False

    CURRENT_TRIAL_FOLDER = BASE_EVAL_NAME+"_"+CURRENT_TRIAL_NAME
    SAVE_FOLDER = os.path.join(BASE_FOLDER,CURRENT_TRIAL_FOLDER)
    CSV_HEADER = [
        "env_idx", 
        "env_type",
        "agent_type"
        "llm_type", 
        "model", 
        "temperature", 
        "success",
        "done",
        "total_reward",
        "num_of_steps", 
        "num_illegal_actions", 
        "num_nothing_happens", 
        "num_repetitions",
        "num_json_dsnt_load",
        "num_multi_json",
        "num_no_json",
        "num_json_and_text",
        "error", 
        "early_stop",
        "keys_removed", 
        "additional_prompt_annotation",
        "trace_file", 
        "prompt_file"
    ]



    #######################################################
    # LOGGING(CSV) Related
    #######################################################
    #CSV FILE Related Things
    MAIN_CSV_FILEPATH = os.path.join(SAVE_FOLDER,MAIN_CSV_FILE_NAME+".csv")

    # Writing the Header 
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
    if CREATE_NEW_LOG_CSV:
        file_counter = 0
        while os.path.exists(MAIN_CSV_FILEPATH):
            MAIN_CSV_FILEPATH = os.path.join(SAVE_FOLDER,MAIN_CSV_FILE_NAME+str(file_counter)+".csv") 
            file_counter+=1 
        # Now that we have a new unique csv file name create it and write the header.
        write_line_to_main_log_csv(MAIN_CSV_FILEPATH, CSV_HEADER)
    else:
        if not os.path.exists(MAIN_CSV_FILEPATH): #Only write header once
            write_line_to_main_log_csv(MAIN_CSV_FILEPATH, CSV_HEADER)




    #######################################################
    # AGENT Related
    #######################################################
    agent, actual_model = get_agent_and_model(llm_type=llm_type, temperature=temperature, proposed_model=model)
    agent.update_save_path(SAVE_FOLDER)

    if actual_model != model:
        print(f"WARNING: Your model:{model} is not used, instead using default model: {actual_model}")
        print("Do you still want to continue? Press 'y' to continue.")
        user_input = input(">")
        if user_input=="y":
            pass
        else:
            exit(1)


    #######################################################
    # ENV Related
    #######################################################
    # Env Init
    with open('playgrounds/base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    split = args.eval_split
    # split = "eval_in_distribution"

    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)
    

    # Skipping Envs 
    for i in range(start_env_idx):
        observation, info = env.reset()
        # name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        # env_type = get_env_type(name)
        # print(name)
        # print(f"Idx: {i} Env:{env_type}")

    # input(">")



    #######################################################
    # RUNNING The Trial
    #######################################################  
    # Running Trial
    for env_idx in range(num_envs):
       

        #######################################################
        # ENV Init
        ####################################################### 
        # Get new environment
        observation, info = env.reset()

        observation = '\n'.join(observation[0].split('\n\n')[1:])
        name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        
        env_type = get_env_type(name)
        # if not env_type=="clean":
        #     continue
        print(f"Starting Env with Index: {env_idx+start_env_idx} of type: {env_type}")

        print(observation)
        observation += "\n"
        # print(info)
        # print(name)


        #######################################################
        # PROMPT Related
        #######################################################     
        keys_to_remove_string, prompt_example, new_base_prompt, num_examples = get_prompt_example(
            react_prompt=REACT_PROMPT,
            agentbench_prompt=AGENTBENCH_PROMPT, 
            jsonreact_prompt=JSON_REACT_PROMPT, 
            swap_order=SWAP_ORDER, 
            num_examples = NUM_EXAMPLES,
            version = VERSION,
            env_type=env_type,
            log_full_prompt = LOG_FULL_PROMPT,
            generate_example=True, 
            keys_to_remove=keys_to_remove)

        prompt = generate_prompt_from_example(prompt_example, number_of_examples=num_examples, base_prompt=new_base_prompt)
        agent.set_base_prompt_and_reset(prompt)

        # ###
        # Save Raw Prompt
        now = datetime.now()
        prompt_save_path = os.path.join(SAVE_FOLDER, "prompt_"+now.strftime("%d_%m_%Y_%H_%M_%S")+".txt")
        

        raw_prompt = generate_prompt_from_example(prompt_example, return_raw_prompt=True, number_of_examples=num_examples, base_prompt=new_base_prompt)
        save_prompt_file(prompt_save_path, raw_prompt)




        # ####################################
        # SETTING the STOP Condition for AGENT
        if NOT_JSON_PROMPTS:
            agent.stop_sequences = ["\n"]
            OUR_PROMPT_ADD_BRACKET_CONDITION=False
        else:
            agent.stop_sequences = ["}\n"]
            OUR_PROMPT_ADD_BRACKET_CONDITION=True




        #######################################################
        # Logging Init & Initial values
        ####################################################### 
        logging_dict = get_empty_dict_from_csv_header(CSV_HEADER)

        logging_dict["env_idx"]  = env_idx+start_env_idx
        logging_dict["env_type"] = env_type
        logging_dict["llm_type"] = llm_type
        logging_dict["agent_type"] = agent_type
        logging_dict["model"] = actual_model
        logging_dict["temperature"] = temperature




        #######################################################
        # GAME VARIABLES AND SETTINGS
        #######################################################   
        # FIXED VARIABLES
        LIMIT = 60
        INPUT_TOKEN = ""
        OUTPUT_TOKEN = ""

        CAPITAL = [chr(x+65) for x in range(26)]
        LOWER = [chr(x+97) for x in range(26)]

        LIMIT_CURRENT_REPETITIONS = 5 #after 5 repetitions stop current run.



        # To be reset at each run.
        game_running_flag = True
        counter = 0
        error = ""
        early_stop = ""
        success = False
        logging_done = False
        total_reward = 0

        num_illegal_actions = 0
        num_nothing_happens = 0
        num_repetitions = 0
        
        num_json_dsnt_load = 0
        num_multi_json = 0
        num_no_json = 0
        num_json_and_text = 0

        prev_action = ""
        num_current_repetitions = 0


        # for resampling
        CURRENT_NOTHING_HAPPENS = False


        #######################################################
        # Main Game Loop
        ####################################################### 
        try:
            while game_running_flag:
                is_illegal_action = False
                is_nothing_happens = False


                # #####################
                # Action related

                # action = input(">")
                action = agent.act(f"{INPUT_TOKEN}"+observation+f"{OUTPUT_TOKEN}")
                # print(action)
                # input(">")

                #Modify Actions
                if OUR_PROMPT_ADD_BRACKET_CONDITION and (not action.endswith("}")):
                    agent.pop_from_history()
                    action+="}"
                    agent.add_to_history(action,"assistant")
                if not action.endswith("\n"):
                    agent.pop_from_history()
                    action+="\n"
                    agent.add_to_history(action,"assistant")

                print("<<< ACTION >>>:"+action)

                # for char in action:
                #     print(ord(char))
                #     print(chr(ord(char)).encode("utf-8"))

                if action.startswith("> "):
                    action = action.replace("> ","")

                if action.startswith(">"):
                    action = action.replace(">","")
                
                # TODO: This is ReAct
                if action.startswith("think:") or '"think": "' in action:
                    observation = "OK.\n"
                    print("<> OBSERVATION <>:"+observation)
                    continue

                if action.startswith('think("'):
                    observation = "You are thinking.\n"
                    print("<> OBSERVATION <>:"+observation)
                    continue

                action_count = action.count('"action"')
                if action_count > 1:
                    num_multi_json += 1
                    appendix = action.split("}")[-1]
                    if any(y in appendix for y in CAPITAL+LOWER):
                        num_json_and_text += 1

                elif action_count == 0:
                    num_no_json += 1


                try:
                    _ = json.loads(action)
                except Exception as e:
                    num_json_dsnt_load += 1


                action, is_illegal_action = process_action(action, track_is_illegal=True)
                # TODO: This is Agentbench
                if "THOUGHT:" in action:
                    observation = "\n"
                    continue

                if is_illegal_action:
                    num_illegal_actions += 1

                if action == prev_action:
                    num_repetitions += 1
                    num_current_repetitions +=1
                else:
                    num_current_repetitions =0

                if CORRECTION:
                    # TODO: maybe start tracking those changes.
                    action = transform_put_action(action)
                    print(f"TRANSFORMED_ACTION:{action}")

                prev_action = action




                # #####################
                # Observation Related
                observation, reward, done, info = env.step([action])
                total_reward += reward[0]


                observation, is_nothing_happens = process_ob(observation[0], track_nothing_happens=True)
                if is_nothing_happens:
                    num_nothing_happens += 1
                    CURRENT_NOTHING_HAPPENS = True
                else:
                    CURRENT_NOTHING_HAPPENS = False


                
                print("<> OBSERVATION <>:"+observation)
                print(info["won"][0])
                print(done[0])
                print(reward[0])

                if done[0] or info["won"][0]:
                    if info["won"][0]:
                        success=True
                    else:
                        success=False

                    if done[0]:
                        logging_done=True 
                    else:
                        logging_done=False

                    break
                    
                counter += 1
                if counter == LIMIT:
                    early_stop = "ENV_ERROR: Reached Step Limit"
                    break

                if num_current_repetitions == LIMIT_CURRENT_REPETITIONS:
                    early_stop = "ENV_ERROR: Too many ({LIMIT_CURRENT_REPETITIONS}) consecutive repetitions."
                    break


        except cohere.core.ApiError as e:
            print("COHERE API ERROR")
            print(e)
            print(e.body)
            error = str(e)

        except Exception as e:
            print("ANOTHER EXCEPTION")
            error = str(e)
            print(error)
            print(e)

        finally:
            logging_dict["num_illegal_actions"] = num_illegal_actions
            logging_dict["num_nothing_happens"] = num_nothing_happens
            logging_dict["num_repetitions"] = num_repetitions

            logging_dict["num_json_dsnt_load"] = num_json_dsnt_load
            logging_dict["num_multi_json"] = num_multi_json
            logging_dict["num_no_json"] = num_no_json
            logging_dict["num_json_and_text"] = num_json_and_text
            logging_dict["num_of_steps"] = counter
            logging_dict["success"] = success
            logging_dict["done"] = logging_done
            logging_dict["total_reward"] = total_reward
            logging_dict["error"] = error
            logging_dict["early_stop"] = early_stop
            logging_dict["keys_removed"] = keys_to_remove_string
            logging_dict["trace_file"] = agent.file_name
            logging_dict["prompt_file"] = prompt_save_path
            logging_dict["additional_prompt_annotation"] = additional_prompt_annotation
            write_line_to_main_log_csv(MAIN_CSV_FILEPATH, logging_dict)
            agent.save()

    