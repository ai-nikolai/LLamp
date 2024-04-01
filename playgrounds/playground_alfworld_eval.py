import yaml
import csv
import os

import cohere

import alfworld
import alfworld.agents.environment

from llamp.anthropic_agent import AnthropicAgent
from llamp.anthropic_text_agent import AnthropicTextAgent

from llamp.cohere_agent import CohereAgent
from llamp.cohere_text_agent import CohereTextAgent
from llamp.cohere_text_chat_agent import CohereTextChatAgent


from llamp.openai_agent import OpenAIAgent
from llamp.openai_text_agent import OpenAITextAgent
from llamp.openai_text_chat_agent import OpenAITextChatAgent


from datetime import datetime

import json



from playground_alfworld_ablation_generator import generate_string_prompt, remove_keys

from playground_alfworld_react_prompt_utils import return_react_examples, return_agentbench_prompts, return_json_react_examples


from alfworld_prompts_utils_v4_clean_base import clean_v4_base, clean_v4_base_2
from alfworld_prompts_utils_v4_cool_base import cool_v4_base, cool_v4_base_2
from alfworld_prompts_utils_v4_examine_base import examine_v4_base, examine_v4_base_2
from alfworld_prompts_utils_v4_heat_base import heat_v4_base, heat_v4_base_2
from alfworld_prompts_utils_v4_put_base import put_v4_base, put_v4_base_2
from alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base, puttwo_v4_base_2



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

ENV_TO_EXAMPLE_MAPPING = {
    "clean" : clean_v4_base,
    "cool"  : cool_v4_base,
    "examine"   : examine_v4_base,
    "heat"  : heat_v4_base,
    "put"   : put_v4_base,
    "puttwo"    : puttwo_v4_base
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
AGENT_MODEL_MAPPING = {
    "Anthropic" : ["claude-2.1"],
    "Cohere" : ["command","command-nightly"],
    "OpenAI" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"],
    "AnthropicText" : ["claude-2.1"],
    "CohereText" : ["command","command-nightly"],
    "OpenAIText" : ["davinci-002", "gpt-3.5-turbo-instruct"],
    "CohereTextChat" : ["command","command-nightly"],
    "OpenAITextChat" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"]
}

def get_agent_and_model(agent_type, temperature=0.0, proposed_model=""):
    """ Returns Agent, Model"""
    #Standard CHAT Models
    if agent_type == "Anthropic":
        model = "claude-2.1"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = AnthropicAgent(temperature=temperature, model=model) 

    elif agent_type == "Cohere":
        # model = "command"
        model = "command-nightly"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereAgent(temperature=temperature, model=model)

    elif agent_type=="OpenAI":
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAIAgent(temperature=temperature, model=model)
 


    #TEXT BASED MODELs
    elif agent_type =="AnthropicText":
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        # model = "claude-1.2"
        model = "claude-2.1"
        agent = AnthropicTextAgent(temperature=temperature, model=model) 

    elif agent_type=="CohereText":
        # model = "command"
        model = "command-nightly"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereTextAgent(temperature=temperature, model=model)

    elif agent_type=="OpenAIText":
        model = "davinci-002"
        model = "gpt-3.5-turbo-instruct"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAITextAgent(temperature=temperature, model=model)     



    #CHAT MODELS used as TEXT MODELs
    elif agent_type=="CohereTextChat":
        # model = "command"
        model = "command-nightly"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = CohereTextChatAgent(temperature=temperature, model=model)


    elif agent_type=="OpenAITextChat":
        model = "gpt-3.5-turbo-0125"
        # model = "gpt-4-turbo-preview"
        if proposed_model:
            if proposed_model in AGENT_MODEL_MAPPING[agent_type]:
                model = proposed_model
            else:
                print("Proposed Model is not available using default model.")
        agent = OpenAITextChatAgent(temperature=temperature, model=model) 


    return agent, model



#################################################################
#Display Settings
#################################################################
def get_settings_string(react_prompt, agentbench_prompt, json_react_prompt, agent_type, model, temperature, num_envs, starting_env, current_trial_name, keys_to_remove, not_ours_param, swap_order, keys_to_remove_string):
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
    display_text += f"   -Algorithm Family: {which_prompt}\n"
    display_text += f"   -AgentType: {agent_type}\n"
    display_text += f"   -Model: {model}\n"
    display_text += f"   -Temperature: {temperature}\n"
    display_text += f"   -Starting env: {starting_env}\n"
    display_text += f"   -Ending env: {starting_env+num_envs-1}\n"
    display_text += f"   -Num of envs: {num_envs}\n"
    display_text += f"   -Current Trial Name: {current_trial_name}\n"
    
    if not not_ours:
        display_text += f"   -Keys that will be removed: {keys_to_remove}\n"
        display_text += f"   -Number of our Prompts: {not_ours_param}\n"  
    if react_prompt:
        display_text += f"   -Number of React Examples: {not_ours_param}\n"  
    if agentbench_prompt:
        display_text += f"   -Prompt Version AgentBench: {not_ours_param}\n"  
    if json_react_prompt:
        display_text += f"   -Number JsonReAct Examples: {not_ours_param}\n" 
    
    # Swap Order
    display_text += f"   -Swap Order of Prompts: {swap_order}\n" 

    #Name of prompt
    display_text += f"   -The prompt will be called: {keys_to_remove_string}\n" 


    display_text += "Do you want to continue? Press 'y' to continue."

    return display_text





#################################################################
#Env Prompt Logic
#################################################################
def get_prompt_example(react_prompt, agentbench_prompt, jsonreact_prompt, swap_order, not_ours_param, env_type, log_full_prompt=False, generate_example=True):
    """ Get name of prompt and example prompts"""
    # Generate correct prompt for this environment (basically pick the right example).  
    new_base_prompt = ""
    swap_string = "-swaped" if swap_order else ""

    #REACT PROMPT or OUR PROMPT
    if react_prompt:
        num_examples = not_ours_param
        if generate_example:
            prompt_example = return_react_examples(env_type, num=num_examples, swap=swap_order)
        keys_to_remove_string = f"react-{num_examples}"+swap_string

    elif agentbench_prompt:
        num_examples = 1
        if generate_example:
            prompt_example, new_base_prompt = return_agentbench_prompts(env_type, return_base=True, version=not_ours_param)
        keys_to_remove_string = f"agentbench-v{not_ours_param}"
        
    elif jsonreact_prompt:            
        num_examples = not_ours_param
        if generate_example:
            prompt_example = return_json_react_examples(env_type, num=num_examples)
        keys_to_remove_string = f"jsonreact-{num_examples}"

    else: #OURS
        num_examples = not_ours_param
        
        if generate_example:
            if swap_order:
                first_prompt_map = ENV_TO_EXAMPLE_MAPPING_2
                second_prompt_map = ENV_TO_EXAMPLE_MAPPING
            else: #the normal case.
                first_prompt_map = ENV_TO_EXAMPLE_MAPPING
                second_prompt_map = ENV_TO_EXAMPLE_MAPPING_2
            base_prompt = remove_keys(first_prompt_map[env_type], keys=keys_to_remove)
            prompt_example = generate_string_prompt(base_prompt)
            
            if num_examples==2:
                base_prompt = remove_keys(second_prompt_map[env_type], keys=keys_to_remove)
                prompt_example2 = generate_string_prompt(base_prompt)
                prompt_example += "\n\n"+prompt_example2

        if log_full_prompt:
            keys_to_remove_string = "+".join(keys_to_remove)
 
        else:
            long_string = "short" if len(keys_to_remove) > 2 else "long"
            keys_to_remove_string = long_string+f"-{num_examples}"+swap_string

    if generate_example:
        return keys_to_remove_string, prompt_example, new_base_prompt, num_examples
    else:
        return keys_to_remove_string










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


    #CHANGE THIS ONE
    CURRENT_TRIAL_NAME = "v2_eval_0-135"
    # CURRENT_TRIAL_NAME = "v2_eval_test_2"


    ###############################
    # Basic Init
    start_env_idx=0
    num_envs = 135

    # start_env_idx=0
    # num_envs = 1

    agent_type = "OpenAITextChat"
    model = "gpt-3.5-turbo-0125"
    temperature = 0.0

    # AGENT_MODEL_MAPPING = {
    #     "Anthropic" : ["claude-2.1"],
    #     "Cohere" : ["command","command-nightly"],
    #     "OpenAI" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"],
    #     "AnthropicText" : ["claude-2.1"],
    #     "CohereText" : ["command","command-nightly"],
    #     "OpenAIText" : ["davinci-002", "gpt-3.5-turbo-instruct"],
    #     "CohereTextChat" : ["command","command-nightly"],
    #     "OpenAITextChat" : ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"]
    # }


    ###############################
    # Which METHOD to run (REACT, AGENTBENCH, OURS)
    REACT_PROMPT = False
    AGENTBENCH_PROMPT = False
    JSON_REACT_PROMPT = False

    SWAP_ORDER = False
    LOG_FULL_PROMPT = False


    #untick for our prompts
    # REACT_PROMPT = True 
    # AGENTBENCH_PROMPT = True
    # JSON_REACT_PROMPT = True

    
    NOT_JSON_PROMPTS = REACT_PROMPT or AGENTBENCH_PROMPT

    # num_examples_react_or_prompt_version_agentbench = 2
    # NOT_OURS_PARAM = num_examples_react_or_prompt_version_agentbench
    
    NOT_OURS_PARAM = 1 #Now this is ours and not ours (naming is legacy)
    SWAP_ORDER = True
    # LOG_FULL_PROMPT = True

    ##############################
    # This applies to our prompts
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
    keys_to_remove = [
        "prompt",
        # "goal", 
        # "plan", 
        "places_visited", 
        "current_inventory", 
        "current_location", 
        "current_objective",
        # "action"
    ]

    keys_to_remove_string2 = get_prompt_example(
        react_prompt=REACT_PROMPT,
        agentbench_prompt=AGENTBENCH_PROMPT, 
        jsonreact_prompt=JSON_REACT_PROMPT, 
        swap_order=SWAP_ORDER, 
        not_ours_param=NOT_OURS_PARAM,
        env_type="",
        log_full_prompt = LOG_FULL_PROMPT,
        generate_example=False)

    ##############################
    # Checking settings with the user. User needs to type y.
    keys_to_remove_string = "+".join(keys_to_remove)
    settings_string = get_settings_string(
            react_prompt = REACT_PROMPT, 
            agentbench_prompt = AGENTBENCH_PROMPT,
            json_react_prompt = JSON_REACT_PROMPT,
            agent_type = agent_type, 
            model = model, 
            temperature = temperature, 
            num_envs = num_envs, 
            starting_env = start_env_idx, 
            current_trial_name = CURRENT_TRIAL_NAME, 
            keys_to_remove=keys_to_remove_string,
            not_ours_param = NOT_OURS_PARAM,
            swap_order = SWAP_ORDER,
            keys_to_remove_string = keys_to_remove_string2
        )
    print(settings_string)
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
    agent, model = get_agent_and_model(agent_type=agent_type, temperature=temperature, proposed_model=model)
    agent.update_save_path(SAVE_FOLDER)




    #######################################################
    # ENV Related
    #######################################################
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
            not_ours_param=NOT_OURS_PARAM,
            env_type=env_type,
            log_full_prompt = LOG_FULL_PROMPT,
            generate_example=True)

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
        logging_dict["agent_type"] = agent_type
        logging_dict["model"] = model
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




        #######################################################
        # Main Game Loop
        ####################################################### 
        try:
            while game_running_flag:
                is_illegal_action = False
                is_nothing_happens = False

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

                prev_action = action

                observation, reward, done, info = env.step([action])
                total_reward += reward[0]


                observation, is_nothing_happens = process_ob(observation[0], track_nothing_happens=True)
                if is_nothing_happens:
                    num_nothing_happens += 1
                
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

    