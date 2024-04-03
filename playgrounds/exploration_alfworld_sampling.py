import yaml
import csv
import os
import json
import re


from llamp.openai_text_chat_agent import OpenAITextChatAgent

from common_utils import (
    write_line_to_main_log_csv,
    get_csv_header_index,
    load_csv_file,
    load_log_file,
    augment_logging_dict
)


import alfworld
import alfworld.agents.environment


import importlib


VERBOSE=False
def print_verbose(*argv,**args):
    if VERBOSE:
        print(*argv,**args)

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
        print_verbose(f"Extracted Action:{action}")

    elif ('"action" : "' in action):
        actions = action.split('"action" : "')
        action = actions[1].split('"')[0]
        print_verbose(f"Extracted Action:{action}")

    elif ('"action": "' in action):
        actions = action.split('"action": "')
        action = actions[1].split('"')[0]
        print_verbose(f"Extracted Action:{action}")

    elif ('"action":"' in action):
        actions = action.split('"action":"')
        action = actions[1].split('"')[0]
        print_verbose(f"Extracted Action:{action}")

    #TODO: this is for AGENTBENCH, need to refactor.
    elif "ACTION:" in action:
        actions = action.split('ACTION:')
        action = actions[1]
        print_verbose(f"Extracted Action:{action}")

    else:
        illegal_action = True

    if track_is_illegal:
        return action, illegal_action
    else:
        return action


def clean_action(action):
    """Returns a clean version of the action"""
    action = action.replace("> ","")
    action = action.replace(">","")
    action = action.replace("\n","")

    if '"action": "' in action:
        action = action.split('"action": "')[1].split('"')[0]

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


def print_actions(interaction_data,current_index):
    """  """
    print_verbose(f"At Index:{current_index}")
    print_verbose(f'Current Action:{interaction_data[current_index]["content"]}')
    if len(interaction_data)>current_index+1:
        print_verbose(f'Next Env Response:{interaction_data[current_index+1]["content"]}')


def extract_content(interaction_data, index):
    """ Extracts the 'content' from the interaction data """
    action_observation = interaction_data[index]["content"]
    return action_observation


def transform_put_action(action):
    """ Put action """
    put_regex_1 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\son(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    put_regex_2 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\sin(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""

    if action.startswith("put"):
        answer = re.match(put_regex_1,action)
        if answer:
            print_verbose("Discovered Put Action with ON only")
            action = action.replace("on","in/on")

        else:
            answer = re.match(put_regex_2,action)
            if answer:
                print_verbose("Discovered Put Action with IN only")
                action = action.replace("in","in/on")
    print_verbose(f"Final Action:{action}")
    return action



def skip_envs(env,skip_envs=0):
    """ skip envs """
    # Skipping Envs 
    for i in range(skip_envs):
        observation, info = env.reset()
        # name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        # env_type = get_env_type(name)
        # print_verbose(name)
        # print_verbose(f"Idx: {i} Env:{env_type}")

    # input(">")
    return env    


def get_new_env():
    """ Returns a new alfworld env """
    importlib.reload(alfworld)
    importlib.reload(alfworld.agents.environment)

    # Env Init
    with open('playgrounds/base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    split = "eval_out_of_distribution"

    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)

    return env   

def start_new_env(env):
    """returns env, observation, env_type """
    observation, info = env.reset()

    observation = '\n'.join(observation[0].split('\n\n')[1:])
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
    
    env_type = get_env_type(name)

    return env, observation, env_type



def main_loop_put(data, data_index, logging_dict, experiment_index=1, current_env_idx=0, env=None):
    """ Runs the put modify loop and records the results."""
    
    # (Re-) Running one experimental run.
    experiment_data = data[experiment_index]
    trace_file_path = experiment_data[data_index["trace_file"]]
    agent_signature = experiment_data[data_index["keys_removed"]]
    
    if not logging_dict.get(agent_signature):
        logging_dict[agent_signature] = 0
    
    if not logging_dict.get(agent_signature+"_modified"):
        logging_dict[agent_signature+"_modified"] = 0

    interaction_history = load_log_file(trace_file_path)

    new_env_idx = int(experiment_data[data_index["env_idx"]])
    
    create_new_env = False

    if new_env_idx <= current_env_idx:
        skip_indices = new_env_idx
        create_new_env = True
    else:
        skip_indices = new_env_idx - (current_env_idx + 1) #plus as we need to account for the rest that happens everyturn anyways.

    current_env_idx = new_env_idx

    current_env_is_success = int(experiment_data[data_index["success"]])

    print(f'Running Experiment with Index: {current_env_idx} the environment was succesful:{current_env_is_success}, need to skip: {skip_indices}')

    #######################################################
    # ENV Related
    #######################################################
    if create_new_env or (not env):
        env = get_new_env()
    
    env = skip_envs(env,skip_indices)



    #######################################################
    # RUNNING The Trial
    #######################################################  
    # Running Trial
    # for env_idx in range(num_envs):
       

    #######################################################
    # ENV Init INDENT FROM HERE
    ####################################################### 

    env, observation, env_type = start_new_env(env)
    print_verbose(f"Starting Env with Index: {current_env_idx} of type: {env_type}")
    print_verbose(observation)

    observation += "\n"
    # print_verbose(obs2)
    obs2 = extract_content(interaction_history, 1)
    assert obs2==observation, "Observations don't match."

    if current_env_is_success:
        logging_dict[agent_signature] += 1
        logging_dict[agent_signature+"_modified"] += 1

    # print_verbose(info)
    # print_verbose(name)



    #######################################################
    # Main Game Loop
    ####################################################### 
    current_history_index = 2

    while True:


        action = extract_content(interaction_history, current_history_index)
        print_actions(interaction_history,current_history_index)

        action = clean_action(action)

        if action.startswith("think:"):
            current_history_index += 2
            continue

        action = transform_put_action(action)

        observation, reward, done, info = env.step([action])
        observation, is_nothing_happens = process_ob(observation[0], track_nothing_happens=True)
        print_verbose(observation)
        print_verbose(done)
        current_history_index += 2

        if done[0] or info["won"][0]:
            if info["won"][0]:
                if current_env_is_success:
                    print_verbose("Both are successful")
                else:
                    print_verbose("====== NEW ENV IS SUCCESSFUL ======")
                    logging_dict[agent_signature+"_modified"] += 1
            break
    return logging_dict, env, current_env_idx




if __name__=="__main__":

    #######################################################
    # Agent Related
    #######################################################
    # temperature = 0
    # model = "gpt-3.5-turbo-0125"
    # agent = OpenAITextChatAgent(temperature=temperature, model=model, save_path="game_logs/experimental/sampling") 

    #######################################################
    # Previous Runs Related
    #######################################################
    data = load_csv_file("playgrounds/all_results.csv")
    data_index = get_csv_header_index(data[0])

    logging_dict = {}
    env=None
    current_env_idx=134

    skip_index = 1
    for idx,experiment in enumerate(data[skip_index:]):
        current_experiment_index = idx+skip_index
        logging_dict, env, current_env_idx = main_loop_put(
                        data=data, 
                        data_index=data_index, 
                        logging_dict=logging_dict, 
                        experiment_index=current_experiment_index,
                        current_env_idx=current_env_idx,
                        env=env
        )
        print(logging_dict)
    print(logging_dict)


        # agent.load_from_saved_data(interaction_history)






# EOF