import os
import json


from prompts.alfworld_prompts_utils_v4_clean_base import clean_v4_base, clean_v4_base_2
from prompts.alfworld_prompts_utils_v4_cool_base import cool_v4_base, cool_v4_base_2
from prompts.alfworld_prompts_utils_v4_examine_base import examine_v4_base, examine_v4_base_2
from prompts.alfworld_prompts_utils_v4_heat_base import heat_v4_base, heat_v4_base_2
from prompts.alfworld_prompts_utils_v4_put_base import put_v4_base, put_v4_base_2
from prompts.alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base, puttwo_v4_base_2

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
            data = json.loads(component)
            if keys:
                for key in keys:
                    data.pop(key, None)
            component = json.dumps(data,indent=2)
        
        out_list.append(component)
    return out_list


if __name__=="__main__":

    all_keys = ["prompt", "goal", "plan", "places_visited", "current_inventory", "current_location", "current_objective", "action"]

    base_prompt = clean_v4_base
    # base_prompt = cool_v4_base
    # base_prompt = examine_v4_base
    # base_prompt = heat_v4_base
    # base_prompt = put_v4_base
    # base_prompt = puttwo_v4_base
    env_types = ["clean","cool","examine","heat","put","puttwo"]
    for env_type in env_types:
        base_prompt = ENV_TO_EXAMPLE_MAPPING[env_type]
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective"])
            result = generate_string_prompt(base_prompt)
        except Exception as e:
            print(env_type)
            print("1 - Error")
            
        base_prompt = ENV_TO_EXAMPLE_MAPPING_2[env_type]        
        try:
            base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective"])
            result = generate_string_prompt(base_prompt)
        except Exception as e:
            print(env_type)
            print("2 - Error")

    # print(result)


