import os
import json


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


if __name__=="__main__":

    all_keys = ["prompt", "goal", "plan", "places_visited", "current_inventory", "current_location", "current_objective", "action"]

    # base_prompt = clean_v4_base_1

    error_flag = False
    alignment_error_flag = False

    env_types = ["clean","cool","examine","heat","put","puttwo"]
    for env_type in env_types:
        base_prompt = ENV_TO_EXAMPLE_MAPPING_0[env_type]
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)
            try:
                react_list = return_json_react_examples(env_type, num=1, first_id=0, version=1, think_key="think", action_key="action", return_list=True)  
                success = verify_react_and_ours(base_prompt, react_list[0])
                    
            except AssertionError as e:
                print("\n======")
                print("0 - Alignmenterror")
                print(env_type)
                print(e)                
                alignment_error_flag=True

        except Exception as e:
            print("======")
            print("0 - Error")
            print(env_type)
            print(e)
            error_flag=True

        base_prompt = ENV_TO_EXAMPLE_MAPPING_1[env_type]
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)

            try:
                react_list = return_json_react_examples(env_type, num=1, first_id=1, version=1, think_key="think", action_key="action", return_list=True)  
                success = verify_react_and_ours(base_prompt, react_list[0])
                    
            except AssertionError as e:
                print("\n======")
                print("1 - Alignmenterror")
                print(env_type)
                print(e)
                alignment_error_flag=True

        except Exception as e:
            print("======")
            print("1 - Error")
            print(env_type)
            print(e)
            error_flag=True

            
        base_prompt = ENV_TO_EXAMPLE_MAPPING_2[env_type]        
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)

            try:
                react_list = return_json_react_examples(env_type, num=1, first_id=2, version=1, think_key="think", action_key="action", return_list=True)  
                success = verify_react_and_ours(base_prompt, react_list[0])
                    
            except AssertionError as e:
                print("\n======")
                print("2 - Alignmenterror")
                print(env_type)
                print(e)
                alignment_error_flag=True

        except Exception as e:
            print("======")
            print("2 - Error")
            print(env_type)
            print(e)
            error_flag=True

    if not error_flag:
        print("No Errors encountered with prompts")
    
    if not alignment_error_flag:
        print("All Prompts align with React")

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

