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
def print_verbose(arg,verbose=VERBOSE):
    if verbose:
        print(arg)

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


def print_actions(interaction_data,current_index,verbose=False):
    """  """
    try:
        print_verbose(f"At Index:{current_index}",verbose)
        print_verbose(f'Current Action:{interaction_data[current_index]["content"]}',verbose)
        if len(interaction_data)>current_index+1:
            print_verbose(f'Next Env Response:{interaction_data[current_index+1]["content"]}',verbose)
    except:
        pass

def extract_content(interaction_data, index):
    """ Extracts the 'content' from the interaction data """
    early_stop=False
    try:
        action_observation = interaction_data[index]["content"]
        return action_observation, early_stop
    except:
        early_stop = True
        return None, early_stop


def transform_put_action(action):
    """ Put action """
    put_regex_1 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\son(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    put_regex_2 = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\sin(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""

    if action.startswith("put"):
        answer = re.match(put_regex_1,action)
        if answer:
            print_verbose("Discovered Put Action with ON only")
            action = action.replace(" on "," in/on ")

        else:
            answer = re.match(put_regex_2,action)
            if answer:
                print_verbose("Discovered Put Action with IN only")
                action = action.replace(" in "," in/on ")
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
    obs2, _ = extract_content(interaction_history, 1)
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


        action, early_stop = extract_content(interaction_history, current_history_index)
        if early_stop:
            logging_dict["failed_early"].append(current_env_idx)
            break
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
            else:
                if current_env_is_success:
                    print(f"------ NEW ENV FAILED:{current_env_idx} -------")
                    logging_dict[agent_signature+"_modified"] -= 1
                logging_dict["failed"].append(current_env_idx)
            break
    return logging_dict, env, current_env_idx


def run_full_analysis(data, data_index):
    """ Runs the full analysis"""
    logging_dict = {}
    env=None
    current_env_idx=134

    logging_dict["failed"] = []
    logging_dict["failed_early"] = []


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
    return logging_dict



def analyse_trace(data, data_index, experiment_index, logging_dict={}, run_game_flag=True):
    """Analyse a single trace."""
    experiment_data = data[experiment_index]
    trace_file_path = experiment_data[data_index["trace_file"]]
    agent_signature = experiment_data[data_index["keys_removed"]]
    env_idx = experiment_data[data_index["env_idx"]]
    env_type = experiment_data[data_index["env_type"]]

    print(f"We are analysing env: {env_idx}, {env_type}")
    if logging_dict.get(env_type):
        logging_dict[env_type] +=1
    else:
        logging_dict[env_type] = 1

    if run_game_flag:
        interaction_history = load_log_file(trace_file_path)
        print_verbose(interaction_history[1]["content"], verbose=True)
        
    current_history_index = 2

    run_game=run_game_flag
    while run_game:
        action, early_stop = extract_content(interaction_history, current_history_index)
        print_actions(interaction_history,current_history_index, verbose=True)
        failure_type = input(">Type Error case to exit env>:")
        if failure_type:
            logging_dict[str(env_idx)+"_"+env_type] = failure_type
            run_game=False
        current_history_index += 2

    return logging_dict

def run_trace_analysis(data, data_index, list_of_interesting_envs,run_game_flag=True):
    """Runs the trace analysis through list of interesting envs"""
    logging_dict = {}
    for index in list_of_interesting_envs:
        logging_dict = analyse_trace(data,data_index,index+1,logging_dict,run_game_flag=run_game_flag)
        print(logging_dict)    
    print(logging_dict)
    return logging_dict

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
    # IN_DATA_FILE = "playgrounds/all_results.csv"
    IN_DATA_FILE = "playgrounds/v2_1_scores.csv"


    data = load_csv_file(IN_DATA_FILE)
    data_index = get_csv_header_index(data[0])
    # logging_dict1 = run_full_analysis(data,data_index)
    

    interesting_envs_failed = [4, 9, 23, 31, 46, 52, 58, 74, 75, 80, 84, 107, 109, 111, 112, 113, 120]
    interesting_envs_failed_early = [19, 35, 40, 51, 63, 66, 70, 71, 72, 77, 79, 89, 99, 103, 130, 132, 133]
    logging_dict2 = run_trace_analysis(data, data_index,interesting_envs_failed_early)
    failed =        {'clean': 6, 'cool': 3, 'puttwo': 6, 'heat': 2}
    failed_early =  {'clean': 4, 'cool': 2, 'puttwo': 4, 'heat': 2, 'put': 2, 'examine': 3}
    print(logging_dict2)

    # data = {'react-1': 16, 'react-1_modified': 64, 'react-2': 43, 'react-2_modified': 81, 'long': 43, 'long_modified': 56, 'short': 44, 'short_modified': 61, 'short-2': 49, 'short-2_modified': 58, 'long-2': 49, 'long-2_modified': 53, 'short-2-swaped': 64, 'short-2-swaped_modified': 68, 'long-2-swaped': 55, 'long-2-swaped_modified': 57, 'react-2-swaped': 55, 'react-2-swaped_modified': 88, 'short-1-swaped': 33, 'short-1-swaped_modified': 41, 'react-1-swaped': 14, 'react-1-swaped_modified': 61, 'long-1-swaped': 30, 'long-1-swaped_modified': 34}



    # agent.load_from_saved_data(interaction_history)


    # We are analysing env: 4, clean
    # We are analysing env: 9, cool
    # We are analysing env: 23, puttwo
    # We are analysing env: 31, cool
    # We are analysing env: 46, clean
    # We are analysing env: 52, heat
    # We are analysing env: 58, clean
    # We are analysing env: 74, puttwo
    # We are analysing env: 75, heat
    # We are analysing env: 80, puttwo
    # We are analysing env: 84, cool
    # We are analysing env: 107, clean
    # We are analysing env: 109, clean
    # We are analysing env: 111, clean
    # We are analysing env: 112, puttwo
    # We are analysing env: 113, puttwo
    # We are analysing env: 120, puttwo

# handtowel 3, clean
# 2 pillows

# fail_data_early={'heat': 2, '19_heat': 'mistakes cup for mug (env error put replacement)', 'put': 2, '35_put': 'mistakes peppershaker for saltshaker (twice) and picks it up in the wrong place', 'puttwo': 4, '40_puttwo': 'finds first toilet paper, goes to cabinet, does not put it in and starts saying it now found the second toiletpaper (although there is none) so should take it, then does not take and looks in more locations until it finds a location that does not have it and tries to take there (i.e. several hallucinations)', '51_puttwo': 'mistakes spraybottle for soapbottle (first one already), but attempts to take soapbottle', 'clean': 4, '63_clean': 'mistakes butterknife for knife (solves correctly)', 'cool': 2, '66_cool': 'does not use "cool" command to cool pan (attempts various things like opening the fridge, "freezer compartment")', '70_put': 'mistakes peppershaker for saltshaker  (explicitly stated this assumption)', 'examine': 3, '71_examine': 'invents object at location (mug), mistakes mug for bowl, then finds desklamp, but did not "remember" it had seen it already.', '72_puttwo': 'solves the first keychain, then invents object keychain at location and starts trying to take it', '77_heat': 'keeps looking for an egg, without a specific plan.', '79_clean': 'x', '89_cool': 'x', '99_puttwo': 'x', '103_clean': 'x', '130_examine': 'x', '132_clean': 'x', '133_examine': 'x'}


# fail_data = {'clean': 6, 
# '4_clean': "handtowel 1 mistaken for desired object cloth, (environment doesn't allow for handtowel to be cleaned in sinkbasin)", 
# 'cool': 3, 
# '9_cool': '"cool" command not used to cool the bread in the fridge, fridge opened, no cool bread seen in the fridge', 
# 'puttwo': 6, 
# '23_puttwo': "both pillows are in the same place, first pillow put on armchair, then system wants to look in new places (doesn't go back to the found pillow)", 
# '31_cool': 'Pan not found, algorithms says "Now I found pan,.." but then suggests to look in places again, suggest the same places (with random indices) again, eg. cabinet 4, drawer 3 (although it saw both already).', 
# '46_clean': "mistakes handtowel for cloth, (environment doesn't allow cleaning handtowel in sinkbasin) and algorithms wants to clean handtowel in a different way afterwards", 
# 'heat': 2, 
# '52_heat': 'mistakes mug for cup, attempts to pick up "cup" a few times when there is only a mug present', 
# '58_clean': 'does not find pan and looks suggests to look in same places again (often with a random starting place, e.g. drawer 3, cabinet 4).', '74_puttwo': 'finds both pillows in the same place and then puts the first one, but looks for the second one in new places afterwards', 
# '75_heat': 'mistakes mug for cup and attempts to take cup when only mug present', 
# '80_puttwo': 'finds two soapbars in same place (env error, wrong put correction)', 
# '84_cool': 'does not use cool command, puts bread in fridge and then does not take it and goes to countertop to put in, fails as bread is not in inventory', 
# '107_clean': 'mistakes handtowel for cloth', 
# '109_clean': 'mistakes handtowel for cloth (and again cleaning at sinkbasin does not work)', 
# '111_clean': 'attempts to put clean soapbard on countertop, but it is at sinkbasin', 
# '112_puttwo': 'finds first peppershaker after a while and brings it to drawer then looks for second peppershaker (in similar places again and again) decides to look in drawer and on second attempt of looking through drawers picks up the first peppershaker and puts it back into drawer', 
# '113_puttwo': 'finds both pillows in same place, puts the first pillow, but then looks for second pillow in new places', 
# '120_puttwo': 'solves first peppershaker, finds and takes second peppershaker, chooses to to go shelf instead of drawer, then changes plan to look for second peppershaker again finds third peppershaker and is unable to take it, as there is second one already'}


# EOF