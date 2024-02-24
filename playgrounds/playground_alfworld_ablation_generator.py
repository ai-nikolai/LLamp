import os
import json


from alfworld_prompts_utils_v4_clean_base import clean_v4_base
from alfworld_prompts_utils_v4_cool_base import cool_v4_base
from alfworld_prompts_utils_v4_examine_base import examine_v4_base
from alfworld_prompts_utils_v4_heat_base import heat_v4_base
from alfworld_prompts_utils_v4_put_base import put_v4_base
from alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base


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


    base_prompt = remove_keys(base_prompt, keys=["prompt","current_objective"])
    result = generate_string_prompt(base_prompt)

    print(result)


