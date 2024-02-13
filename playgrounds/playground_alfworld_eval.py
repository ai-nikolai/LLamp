import yaml
import csv
import os

import cohere

import alfworld
import alfworld.agents.environment

from llamp.cohere_agent import CohereAgent
from llamp.openai_agent import OpenAIAgent

# import importlib
# importlib.reload(alfworld)
# importlib.reload(alfworld.agents.environment)

from alfworld_prompts_utils import clean_simple_goal_plan_1, \
cool_simple_goal_plan_1, \
examine_simple_goal_plan_1, \
heat_simple_goal_plan_1, \
clean_state_goal_plan_1, \
clean_state_goal_plan_v2_1, \
clean_state_goal_plan_v3_1#, \
# clean_state_goal_plan_v4_1, \
# clean_state_goal_plan_v4b_1, \
# clean_state_goal_plan_v4c_1, \
# clean_state_goal_plan_v4d_1, \
# clean_state_goal_plan_v4e_1, \
# clean_state_goal_plan_v4f_1, \
# clean_state_goal_plan_v4g_1, \
# clean_state_goal_plan_v4h_1

from alfworld_prompts_utils_v4 import \
clean_state_goal_plan_v4_1, \
clean_state_goal_plan_v4b_1, \
clean_state_goal_plan_v4c_1, \
clean_state_goal_plan_v4d_1, \
clean_state_goal_plan_v4e_1, \
clean_state_goal_plan_v4f_1, \
clean_state_goal_plan_v4g_1, \
clean_state_goal_plan_v4h_1


ENV_TYPES = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
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

    if track_nothing_happens:
        return ob, nothing_happens
    else:
        return ob


def generate_prompt_from_example(example):
    """ Generates prompt """
    prompt = [{
                "role" : "system",
                "content" : f"""
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


For example:
<<<
{example}
>>>

A few hints:
<<<
If "Nothing happens.", then try a valid action that you have not tried before.
Some actions can be only executed in specific places, such as cleaning, heating, cooling...
Learn from the example.
Generate just one JSON output.
>>>
"""
            }]

    return prompt


def write_line_to_main_log_csv(name, data):
    """Writes one line of output into the main CSV"""
    with open(name, 'a', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if type(data) == list:
            wr.writerow(data)
        elif type(data) == dict:
            data_list = [x for _,x in data.items()]
            wr.writerow(data_list)
  

def get_empty_dict_from_csv_header(header):
    """Generate empty dict from csv header"""
    out_dict = {}
    for column_name in header:
        out_dict[column_name] = ""
    return out_dict


if __name__=="__main__":
    # Global Variables 
    # Config File as input (@Marek Idea)
    SAVE_FOLDER = "game_logs/alfworld_eval_10"
    CSV_HEADER = ["env_idx", "env_type", "agent_type", "model", "temperature", "success", "num_of_steps", "num_illegal_actions", "num_nothing_happens", "num_repetitions","error", "trace_file", "prompt_file"]
    MAIN_CSV_FILE_NAME = "alfworld_results"
    CREATE_NEW_LOG_CSV=False    

    # Basic Init
    start_env_idx=0
    num_envs = 10
    agent_index = 1
    temperature = 0.8

    if agent_index == 1:
        agent_type = "Cohere"
        model = "command"
        agent = CohereAgent(temperature=temperature)
    elif agent_index==2:
        agent_type = "OpenAI"
        model = "gpt-3.5-turbo-0125"
        agent = OpenAIAgent(temperature=temperature, model="gpt-3.5-turbo-0125")


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
        if not env_type=="clean":
            continue
        print(f"Starting Env with Index: {env_idx+start_env_idx} of type: {env_type}")

        # Generate correct prompt for this environment (basically pick the right example).
        prompt = generate_prompt_from_example(clean_state_goal_plan_v4g_1)
        agent.set_base_prompt_and_reset(prompt)


        print(observation)
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
        LIMIT = 20
        error = ""
        success = False
        num_illegal_actions = 0
        num_nothing_happens = 0
        num_repetitions = 0
        try:
            while game_running_flag:
                prev_action = ""
                is_illegal_action = False
                is_nothing_happens = False

                # action = input(">")
                action = agent.act("Input:\n"+observation)
                print("<<< ACTION >>>:"+action)
                if action.startswith("think:"):
                    observation = "You are thinking. Please take an action."
                    continue
                if action.startswith('think("'):
                    observation = "You are thinking."
                    continue

                action, is_illegal_action = process_action(action, track_is_illegal=True)
                if is_illegal_action:
                    num_illegal_actions += 1

                if action == prev_action:
                    num_repetitions += 1

                observation, reward, done, info = env.step([action])
                # print(observation)

                observation, is_nothing_happens = process_ob(observation[0], track_nothing_happens=True)
                if is_nothing_happens:
                    num_nothing_happens += 1
                print("<> OBSERVATION <>:"+observation)
                print(info["won"][0])
                print(done[0])
                if done[0]:
                    success = True
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
            logging_dict["num_of_steps"] = counter
            logging_dict["success"] = success
            logging_dict["error"] = error
            logging_dict["trace_file"] = agent.file_name
            write_line_to_main_log_csv(MAIN_CSV_FILEPATH, logging_dict)
            agent.save()

    