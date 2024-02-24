import yaml
import csv
import os

import cohere

import alfworld
import alfworld.agents.environment

from llamp.cohere_agent import CohereAgent
from llamp.openai_agent import OpenAIAgent
from llamp.cohere_text_agent import CohereTextAgent
from llamp.openai_text_agent import OpenAITextAgent

from datetime import datetime

import json

# import importlib
# importlib.reload(alfworld)
# importlib.reload(alfworld.agents.environment)

# from alfworld_prompts_utils import clean_simple_goal_plan_1, \
# cool_simple_goal_plan_1, \
# examine_simple_goal_plan_1, \
# heat_simple_goal_plan_1, \
# clean_state_goal_plan_1, \
# clean_state_goal_plan_v2_1, \
# clean_state_goal_plan_v3_1#, \
# # clean_state_goal_plan_v4_1, \
# # clean_state_goal_plan_v4b_1, \
# # clean_state_goal_plan_v4c_1, \
# # clean_state_goal_plan_v4d_1, \
# # clean_state_goal_plan_v4e_1, \
# # clean_state_goal_plan_v4f_1, \
# # clean_state_goal_plan_v4g_1, \
# # clean_state_goal_plan_v4h_1

# from alfworld_prompts_utils_v4_clean import \
# clean_state_goal_plan_v4a_1, \
# clean_state_goal_plan_v4b_1, \
# clean_state_goal_plan_v4c_1, \
# clean_state_goal_plan_v4d_1, \
# clean_state_goal_plan_v4e_1, \
# clean_state_goal_plan_v4f_1, \
# clean_state_goal_plan_v4g_1, \
# clean_state_goal_plan_v4h_1, \
# clean_state_goal_plan_v4i_1

from playground_alfworld_ablation_generator import generate_string_prompt, remove_keys

from alfworld_prompts_utils_v4_clean_base import clean_v4_base
from alfworld_prompts_utils_v4_cool_base import cool_v4_base
from alfworld_prompts_utils_v4_examine_base import examine_v4_base
from alfworld_prompts_utils_v4_heat_base import heat_v4_base
from alfworld_prompts_utils_v4_put_base import put_v4_base
from alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base

ENV_TYPES = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
} 

ENV_TO_EXAMPLE_MAPPING = {
    "clean" : clean_v4_base,
    "cool"  : cool_v4_base,
    "examine"   : examine_v4_base,
    "heat"  : heat_v4_base,
    "put"   : put_v4_base,
    "puttwo"    : puttwo_v4_base
}

from playground_alfworld_react_prompt_utils import return_react_examples

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


HINTS="""
A few hints:
<<<
1. When "Nothing happens." this means your action was not successful or not valid. If this happen, then try a valid action that you have not tried before.

2. If you repeat yourself, try a different valid action. 

3. Visit new places to find an object.

4. Some actions can be only executed in specific places, such as cleaning, heating, cooling...

5. Be literatal.

6. Initially you have not visited any places and you are starting at the 'starting_location'.

7. Generate one JSON output only.
>>>
"""

HINTS=""
def generate_prompt_from_example(examples, return_raw_prompt = False, number_of_examples=1):
    """ Generates prompt """
    if number_of_examples >1:
        s_string="s"
    else:
        s_string=""
    number_of_examples_string = str(number_of_examples)


    raw_prompt = f"""
You will interact with the environment to solve the given task.

This is the list of all valid actions that you can use:
<<<
- go to <dir> [example: go to table 1]
- open <obj> [example: open door 1]
- close <obj> [example: close door 1]
- put <obj> in/on <obj> [example: put apple 1 in/on table 1]
- take <obj> from <obj> [example: take apple 1 from table 1]
- cool <obj> with <obj> [example: cool apple 1 with fridge 1]
- heat <obj> with <obj> [example: heat apple 1 with fire 1]
- use <obj> [example: use desklamp 1]
>>>


Here is {number_of_examples_string} example{s_string}:
<<<
{examples}
>>>

{HINTS}

"""
# This is the current Interaction:

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



REACT_PROMPT = False
if __name__=="__main__":
    # Global Variables 
    # Config File as input (@Marek Idea)

    REACT_PROMPT = True #untick for our prompts
    BASE_FOLDER = "game_logs"
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_react_4"
    SAVE_FOLDER = os.path.join(BASE_FOLDER,CURRENT_TRIAL_FOLDER)
    CSV_HEADER = [
        "env_idx", 
        "env_type", 
        "agent_type", 
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
        "keys_removed", 
        "trace_file", 
        "prompt_file"
    ]
    MAIN_CSV_FILE_NAME = "alfworld_results"
    CREATE_NEW_LOG_CSV=False

    # Basic Init
    start_env_idx=0
    num_envs = 10

    agent_index = 4
    temperature = 0.0

    if agent_index == 1:
        agent_type = "Cohere"
        # model = "command"
        model = "command-nightly"
        agent = CohereAgent(temperature=temperature, model=model)
    elif agent_index==2:
        agent_type = "OpenAI"
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        agent = OpenAIAgent(temperature=temperature, model=model)
    elif agent_index==3:
        agent_type = "CohereText"
        model = "command"
        agent = CohereTextAgent(temperature=temperature, model=model)
    elif agent_index==4:
        agent_type = "OpenAIText"
        model = "davinci-002"
        agent = OpenAITextAgent(temperature=temperature, model=model)     


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


    agent.update_save_path(SAVE_FOLDER)

    # Env Init
    with open('playgrounds/base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    split = "eval_out_of_distribution"

    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)
    

    # Skipping Envs 
    for i in range(start_env_idx):
        observation, info = env.reset()
        # name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        # env_type = get_env_type(name)
        # print(name)
        # print(env_type)
    
    # Running Trial
    for env_idx in range(num_envs):
        logging_dict = get_empty_dict_from_csv_header(CSV_HEADER)

        # Get new environment
        observation, info = env.reset()

        observation = '\n'.join(observation[0].split('\n\n')[1:])
        name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        
        env_type = get_env_type(name)
        # if not env_type=="clean":
        #     continue
        print(f"Starting Env with Index: {env_idx+start_env_idx} of type: {env_type}")

        # Generate correct prompt for this environment (basically pick the right example).  
        keys_to_remove = [
            "prompt",
            # "goal", 
            # "plan", 
            # "places_visited", 
            # "current_inventory", 
            # "current_location", 
            "current_objective",
            # "action"
        ]
        # keys_to_remove = [
        #     "prompt",
        #     # "goal", 
        #     # "plan", 
        #     "places_visited", 
        #     "current_inventory", 
        #     "current_location", 
        #     "current_objective",
        #     # "action"
        # ]

        keys_to_remove_string = "+".join(keys_to_remove)
        # prompt_keys_for_reference = ["prompt", "goal", "plan", "places_visited", "current_inventory", "current_location", "current_objective", "action"]
        
        base_prompt = remove_keys(ENV_TO_EXAMPLE_MAPPING[env_type], keys=keys_to_remove)
        prompt_example = generate_string_prompt(base_prompt)

        #REACT PROMPT
        if REACT_PROMPT:
            num_examples = 2
            prompt_example = return_react_examples(env_type, num=num_examples)  
        else:
            num_examples = 1

        # prompt_example = clean_state_goal_plan_v4i_1

        prompt = generate_prompt_from_example(prompt_example, number_of_examples=num_examples)
        agent.set_base_prompt_and_reset(prompt)

        # Save Raw Prompt
        now = datetime.now()
        prompt_save_path = os.path.join(SAVE_FOLDER, "prompt_"+now.strftime("%d_%m_%Y_%H_%M_%S")+".txt")
        


        raw_prompt = generate_prompt_from_example(prompt_example, return_raw_prompt=True, number_of_examples=num_examples)
        save_prompt_file(prompt_save_path, raw_prompt)


        print(observation)
        observation += "\n"
        # print(info)
        # print(name)

        logging_dict["env_idx"]  = env_idx+start_env_idx
        logging_dict["env_type"] = env_type
        logging_dict["agent_type"] = agent_type
        logging_dict["model"] = model
        logging_dict["temperature"] = temperature



        # To be reset at each run.
        game_running_flag = True
        counter = 0
        LIMIT = 60
        error = ""
        success = False
        done = False
        total_reward = 0

        num_illegal_actions = 0
        num_nothing_happens = 0
        num_repetitions = 0
        
        num_json_dsnt_load = 0
        num_multi_json = 0
        num_no_json = 0
        num_json_and_text = 0

        prev_action = ""

        INPUT_TOKEN = ""
        OUTPUT_TOKEN = ""

        CAPITAL = [chr(x+65) for x in range(26)]
        LOWER = [chr(x+97) for x in range(26)]

        agent.stop_sequences = ["\n"]
        try:
            while game_running_flag:
                is_illegal_action = False
                is_nothing_happens = False

                # action = input(">")
                action = agent.act(f"{INPUT_TOKEN}"+observation+f"{OUTPUT_TOKEN}")
                
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

                if action.startswith("think:"):
                    observation = "OK.\n"
                    continue

                if action.startswith('think("'):
                    observation = "You are thinking.\n"
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
                if is_illegal_action:
                    num_illegal_actions += 1

                if action == prev_action:
                    num_repetitions += 1
                    prev_action = action

                observation, reward, done, info = env.step([action])
                total_reward += reward[0]

                observation, is_nothing_happens = process_ob(observation[0], track_nothing_happens=True)
                if is_nothing_happens:
                    num_nothing_happens += 1
                
                print("<> OBSERVATION <>:"+observation)
                print(info["won"][0])
                print(done[0])

                if done[0]:
                    done = True
                    if info["won"][0]: #done[0] is actually false
                        success = True  
                    break
                    
                if info["won"][0]: #done[0] is actually false
                    success = True
                    if done[0]:
                        done=True
                    break

                counter += 1
                if counter == LIMIT:
                    error = "ENV_ERROR: Reached Step Limit"
                    break
        except cohere.error.CohereAPIError as e:
            print("COHERE API ERROR")
            error = e.message
            print(e.message)

        except Exception as e:
            print("ANOTHER EXCEPTION")
            error = str(e)
            print(e)
            print(e.message)
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
            logging_dict["done"] = done
            logging_dict["total_reward"] = total_reward
            logging_dict["error"] = error
            logging_dict["keys_removed"] = keys_to_remove_string
            logging_dict["trace_file"] = agent.file_name
            logging_dict["prompt_file"] = prompt_save_path
            write_line_to_main_log_csv(MAIN_CSV_FILEPATH, logging_dict)
            agent.save()

    