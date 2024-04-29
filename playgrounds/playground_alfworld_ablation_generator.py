import os
import json
import re


from prompts.alfworld_prompts_utils_v4_clean_base import clean_v4_base_0, clean_v4_base_1, clean_v4_base_2
from prompts.alfworld_prompts_utils_v4_cool_base import cool_v4_base_0, cool_v4_base_1, cool_v4_base_2
from prompts.alfworld_prompts_utils_v4_examine_base import examine_v4_base_0, examine_v4_base_1, examine_v4_base_2
from prompts.alfworld_prompts_utils_v4_heat_base import heat_v4_base_0, heat_v4_base_1, heat_v4_base_2
from prompts.alfworld_prompts_utils_v4_put_base import put_v4_base_0, put_v4_base_1, put_v4_base_2
from prompts.alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base_0, puttwo_v4_base_1, puttwo_v4_base_2

from playground_alfworld_react_prompt_utils import return_react_examples, return_agentbench_prompts, return_json_react_examples


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

def generate_string_prompt(base_prompt, system_prefix="", agent_prefix=">"):
    """ Generate simple prompt based on the base."""
    base_prompt = remove_keys(base_prompt)
    prompt=""
    for idx, component in enumerate(base_prompt):
        if idx % 2 == 0:
            prefix = system_prefix
        else:
            prefix = agent_prefix
        
        prompt+=prefix + component + '\n\n'

    return prompt


def remove_keys(base_prompt, keys=[]):
    """Removes keys from the prompt and returns a base prompt."""
    out_list = []
    for idx, component in enumerate(base_prompt):
        if idx % 2 == 1:
            try:
                data = json.loads(component)
                if keys:
                    for key in keys:
                        data.pop(key, None)
                component = json.dumps(data,indent=2)
            except Exception as e:
                print(idx)
                raise e
        
        out_list.append(component)
    return out_list


def get_string_difference(string1, string2):
    """ Gets you the string difference """

    out_string = ""
    if len(string1) > len(string2):
        longer_string = string1
        shorter_string = string2
        longer_str = "1"
    elif len(string1) < len(string2):
        longer_string = string2
        shorter_string = string1
        longer_str = "2"

    else:
        longer_string = string1
        shorter_string = string2   
        same_length = True
        longer_str = "Same"


    for idx, char in enumerate(longer_string):
        if idx < len(shorter_string):
            if not char == shorter_string[idx]:
                out_string += f"Char different at: {idx}, s1:{char} s2:{shorter_string[idx]}\n"
        else:
            out_string += f"The {longer_str} is longer: len1:{len(string1)}, len2:{len(string2)}\n"

    # return out_string
    return None


def verify_react_and_ours(our_prompt, react_prompt):
    """ 
    Assumes that our prompts are a: 
        - list of Observation, Sys Response, 
        - where sys response is a json with various keys

    Assumes that react prompts are the "version1" variant:
        - a list of Observation, sys response
        - where sys response contains either the "think" or "action" key.
    """
    all_true = True
    thinking_count = 0

    for idx, observation in enumerate(our_prompt):

        if idx % 2 ==0:
            react_observation = react_prompt[idx+thinking_count*2]
            assertion1 = observation == react_observation
            if not assertion1:
                difference = get_string_difference(observation, react_observation)
            assert assertion1, f"\n===\nEnv Obs do not allign:\nidx:{idx}\n---\nobs:\n{observation}\n---\nreact:\n{react_observation}\n---\ndifference:\n{difference}"

        else:
            react_thought = ""
            our_state = json.loads(observation)
            react_state = json.loads(react_prompt[idx+thinking_count*2])
            while react_state.get("think"):
                react_thought += react_state["think"]+" "
                thinking_count += 1
                react_state = json.loads(react_prompt[idx+thinking_count*2])

            assertion2 = our_state["thought"] == react_thought.strip()
            if not assertion2:
                difference = get_string_difference(our_state["thought"], react_thought.strip())
            assert assertion2, f'\n===\nThoughts do not allign:\nidx:{idx}\n---\nobs:\n{our_state["thought"]}\n---\nreact:\n{react_thought.strip()}\n---\ndifference:\n{difference}'
            
            assertion3 = our_state["action"] == react_state["action"]
            if not assertion3:
                difference = get_string_difference(our_state["action"], react_state["action"])
            assert assertion3, f'\n===\nActions do not allign:\nidx:{idx}\n---\nobs:\n{our_state["action"]}\n---\nreact:\n{react_state["action"]}\n---\ndifference:\n{difference}'

    return all_true


def extract_react_command_and_arguments(action_string):
    """ 
    Extracts the react command and arguments 
    
    WARNGING: 
        At the moment:
        Only extract commands that change the state, otherwise returns None.

    Regex Builder: https://regex101.com/r/BK3La8/1
    """
    # State changing regex expressions.
    put_regex = """put\s(\w+(?:\s\w+)?\s\d+)\sin\/on\s(\w+(?:\s\w+)?\s\d+)"""
    goto_regex = """go\sto\s(\w+(?:\s\w+)?\s\d+)"""
    take_regex = """take\s(\w+(?:\s\w+)?\s\d+)\sfrom\s(\w+(?:\s\w+)?\s\d+)"""
    
    # #Commands that do not change the state
    # TODO they need to be update to extract arguments correctly.
    # open_regex = """open(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""    
    # cool_regex = """cool(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # clean_regex = """clean(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # use_regex = """use(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # heat_regex = """heat(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # examine_regex = """examine(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # close_regex = """close(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # look_regex = """look"""

    # changing_regexes = [put_regex, goto_regex, take_regex]

    answer = re.match(put_regex,action_string)
    if answer: #Put case
        put_object = answer.group(1)
        put_place = answer.group(2)
        return "put", put_object, put_place

    answer = re.match(goto_regex,action_string)
    if answer: #Put case
        goto_place = answer.group(1)
        return "goto", goto_place, None  

    answer = re.match(take_regex,action_string)
    if answer: #Put case
        take_object = answer.group(1)
        take_place = answer.group(2)
        return "take", take_object, take_place

    # Otherwise return nothing (as it's not changing the state)
    return None, None, None


def update_reference_state_with_action(reference_state, action_string):
    """ Update the reference state with a given command. """
    command, arg1, arg2 = extract_react_command_and_arguments(action_string)

    if command == "goto":
        reference_state["current_location"] = arg1
        reference_state["places_visited"].append(arg1)
    
    if command == "put":
        # TODO check one actually carries this object.
        reference_state["current_inventory"] = ""

    if command == "take":
        # TODO check one can actually take this object. (harder)
        reference_state["current_inventory"] = arg1


def verify_state_tracking(our_prompt):
    """ 
    Assumes that our prompts are a: 
        - list of Observation, Sys Response, 
        - where sys response is a json with various keys
    """
    reference_state = {
        "places_visited": [],
        "current_location": "starting location",
        "current_inventory": ""
    }
    keys_to_check = ["current_location","places_visited","current_inventory"]    
   
    for idx, response in enumerate(our_prompt):
        if idx % 2 == 1:
            our_state = json.loads(response)
            # try:
            for key in keys_to_check:
                assert reference_state[key] == our_state[key],f"States are not the same for: {key} at idx:{idx}\nOurs:\n{our_state[key]}\nTheirs:\n{reference_state[key]}"
            # except AssertionError as e:
            #     print("="*8)
            #     print(f"IDX:{idx} Failed")
            #     print(e)
            
            our_action = our_state["action"]
            update_reference_state_with_action(reference_state, our_action)


if __name__=="__main__":

    all_keys = ["prompt", "goal", "plan", "places_visited", "current_inventory", "current_location", "current_objective", "action"]

    # base_prompt = clean_v4_base_1
    error_flag = False
    alignment_error_flag = False
    state_error_flag = False

    env_mappings = [ENV_TO_EXAMPLE_MAPPING_0, ENV_TO_EXAMPLE_MAPPING_1, ENV_TO_EXAMPLE_MAPPING_2]

    env_types = ["clean","cool","examine","heat","put","puttwo"]


    for env_type in env_types:
        for env_idx,env_mapping in enumerate(env_mappings):
            base_prompt = env_mapping[env_type]
            try:
                base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
                result = generate_string_prompt(base_prompt)

                try:
                    verify_state_tracking(base_prompt)
                except AssertionError as e:
                    print("\n======")
                    print(f"{env_idx} - StateTrackingError")
                    print(env_type)
                    print(e)  
                    state_error_flag = True 

                try:
                    react_list = return_json_react_examples(env_type, num=1, first_id=env_idx, version=1, think_key="think", action_key="action", return_list=True)  
                    success = verify_react_and_ours(base_prompt, react_list[0])
                        
                except AssertionError as e:
                    print("\n======")
                    print(f"{env_idx} - AlignmentError")
                    print(env_type)
                    print(e)                
                    alignment_error_flag=True

            except Exception as e:
                print("======")
                print(f"{env_idx} - Error")
                print(env_type)
                print(e)
                error_flag=True

    if not error_flag:
        print("All prompts in correct format and generate correct strings.")
    
    if not alignment_error_flag:
        print("All Prompts align with React")

    if not state_error_flag:
        print("All States tracked correctly")

    error_present = any([error_flag, alignment_error_flag, state_error_flag])
    if not error_present:
        print("==")
        print("ALL Manual TESTS PASSED")


    # print(result)

    # 0 - cool
    # 2 - heat

# """The fridge 1 is closed.""",

    # #########################
    # TO DEBUG SPECIFIC ENVS:
    # #########################

    # env_type = "cool"
    # example_index = 0
    # react_example = return_react_examples(env_type, num=1,  first_id=example_index)
    # # react_example = return_json_react_examples(env_type, num=1, first_id=example_index, version=2, think_key="think", action_key="action")  
    # print("=-"*10)
    # print(react_example)
    # if example_index==0:
    #     base_prompt = ENV_TO_EXAMPLE_MAPPING_0[env_type]
    # elif example_index==1:
    #     base_prompt = ENV_TO_EXAMPLE_MAPPING_1[env_type]
    # elif example_index==2: 
    #     base_prompt = ENV_TO_EXAMPLE_MAPPING_2[env_type]

    # print("++++")
    # base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","goal","plan","places_visited","current_inventory","current_location"])
    # result = generate_string_prompt(base_prompt)
    # print(result)

# EOF

