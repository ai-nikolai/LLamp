import json
import os

from llamp.utils import cohere_model, openai_model

from prompts.alfworld_prompts_utils_v4_clean_base import clean_v4_base_1, clean_v4_base_2
from prompts.alfworld_prompts_utils_v4_cool_base import cool_v4_base_1, cool_v4_base_2
from prompts.alfworld_prompts_utils_v4_examine_base import examine_v4_base_1, examine_v4_base_2
from prompts.alfworld_prompts_utils_v4_heat_base import heat_v4_base_1, heat_v4_base_2
from prompts.alfworld_prompts_utils_v4_put_base import put_v4_base_1, put_v4_base_2
from prompts.alfworld_prompts_utils_v4_puttwo_base import puttwo_v4_base_1, puttwo_v4_base_2

ENV_TO_EXAMPLE_MAPPING = {
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

from playground_alfworld_ablation_generator import generate_string_prompt

# cohere = cohere_model()
openai = openai_model(model="gpt-4-turbo-preview")



def generate_prompt(prompt_example, target_trace, prompt_trace):
    """ Generate Prompt based on example prompt and desired trace """
    prompt = f"""
Your task is to change the whole input trace into the correct output format.

Here is an example of how the output should look like given the input:
Example Input Trace:
\"
{prompt_trace}
\"
    
Example Output:
\"
{prompt_example}
\"


Input Trace:
\"
{target_trace}
\"
"""
    # print(prompt)

    result = openai(prompt=prompt)
    # result = cohere(prompt=prompt)

    return result


def get_variable_name(env_type, current_index, base_variable_name="state_goal_plan_v4", appendix="_1"):
    """Generates consisten variable names."""
    variable_name = f"{env_type}_{base_variable_name}{chr(97+current_index)}{appendix}"
    return variable_name


if __name__=="__main__":


    types_of_envs = ["clean","cool","examine", "heat", "put", "puttwo"]


    react_prompt_file = "playgrounds/prompts/alfworld_react_prompts_original_v3.json"
    with open(react_prompt_file, "r") as file:
        original_prompts = json.load(file)

    env_type = types_of_envs[4]
    env_type = "puttwo"


    prompt_trace = original_prompts[f"react_{env_type}_1"]
    target_trace = original_prompts[f"react_{env_type}_0"]


    # example_prompt = clean_state_goal_plan_v4i_1
    example_prompt = generate_string_prompt(ENV_TO_EXAMPLE_MAPPING[env_type])
    result = generate_prompt(example_prompt, target_trace, prompt_trace)

    print(example_prompt)
    print(prompt_trace)
    print(target_trace)  
    print(result)


    # with open(file_path, "w") as file:
    #     for index, prompt_example in enumerate(list_of_prompts):
    #         # example_prompt = clean_state_goal_plan_v4i_1
    #         example_prompt = prompt_example
    #         variable_name = get_variable_name(env_type, index)

    #         # result = prompt_example
    #         print(f"Generating for env:{env_type}, index:{index}")
    #         result = generate_prompt(example_prompt, target_trace, prompt_trace)
    #         print(f"Finished Generating")
    #         print(result)

    #         print(f"Writing to file:{file_path} for variable:{variable_name}")
    #         file.write("\n"+variable_name+"="+'"""'+result+'"""\n\n')
    #         print("Finished Writing")


# Replace:
# 1. `\n\n>{` with `""",\n"""{`
# \n\n>{
# """,\n"""{
# 2. `}\n\n` with `}""",\n"""`
# }\n\n
# }""",\n"""

# Replace (v2):
# 1. `\n\n{` with `""",\n"""{`
# 2. `}\n\n` with `}""",\n"""`
 
