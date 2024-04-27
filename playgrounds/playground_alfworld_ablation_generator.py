import os
import json


from prompts.alfworld_prompts_utils_v4_clean_base import clean_v4_base_0, clean_v4_base_1, clean_v4_base_2
from prompts.alfworld_prompts_utils_v4_cool_base import cool_v4_base_0, cool_v4_base_1, cool_v4_base_2
from prompts.alfworld_prompts_utils_v4_examine_base import examine_v4_base_0, examine_v4_base_1, examine_v4_base_2
from prompts.alfworld_prompts_utils_v4_heat_base import heat_v4_base_0, heat_v4_base_1, heat_v4_base_2
from prompts.alfworld_prompts_utils_v4_put_base import put_v4_base_0, put_v4_base_1, put_v4_base_2
from prompts.alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base_0, puttwo_v4_base_1, puttwo_v4_base_2


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


if __name__=="__main__":

    all_keys = ["prompt", "goal", "plan", "places_visited", "current_inventory", "current_location", "current_objective", "action"]

    # base_prompt = clean_v4_base_1

    error_flag = False
    env_types = ["clean","cool","examine","heat","put","puttwo"]
    for env_type in env_types:
        base_prompt = ENV_TO_EXAMPLE_MAPPING_0[env_type]
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)
        except Exception as e:
            print(env_type)
            print("0 - Error")
            print(e)
            error_flag=True

        base_prompt = ENV_TO_EXAMPLE_MAPPING_1[env_type]
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)
        except Exception as e:
            print(env_type)
            print("1 - Error")
            print(e)
            error_flag=True

            
        base_prompt = ENV_TO_EXAMPLE_MAPPING_2[env_type]        
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective","non-existant-key"])
            result = generate_string_prompt(base_prompt)
        except Exception as e:
            print(env_type)
            print("2 - Error")
            print(e)
            error_flag=True

    if not error_flag:
        print("No Errors encountered with prompts")

    # print(result)


