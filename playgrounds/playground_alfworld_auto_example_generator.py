import json
import os

from llamp.utils import cohere_model, openai_model

from alfworld_prompts_utils import clean_simple_goal_plan_1, \
cool_simple_goal_plan_1, \
examine_simple_goal_plan_1, \
heat_simple_goal_plan_1, \
clean_state_goal_plan_1, \
clean_state_goal_plan_v2_1, \
clean_state_goal_plan_v3_1, \
clean_state_goal_plan_v4_1, \
clean_state_goal_plan_v4b_1


from alfworld_prompts_utils_v4_clean import \
clean_state_goal_plan_v4a_1, \
clean_state_goal_plan_v4b_1, \
clean_state_goal_plan_v4c_1, \
clean_state_goal_plan_v4d_1, \
clean_state_goal_plan_v4e_1, \
clean_state_goal_plan_v4f_1, \
clean_state_goal_plan_v4g_1, \
clean_state_goal_plan_v4h_1, \
clean_state_goal_plan_v4i_1

from alfworld_prompts_utils_v4_clean_base import clean_v4_base
from alfworld_prompts_utils_v4_examine_base import examine_v4_base


from playground_alfworld_ablation_generator import generate_string_prompt

# cohere = cohere_model()
openai = openai_model(model="gpt-4-turbo-preview")



def generate_prompt(prompt_example, target_trace, prompt_trace):
    """ Generate Prompt based on example prompt and desired trace """
    prompt = f"""
Your task is to change the whole input trace into the correct format.

Here is an example of how the output should look like:
<<<
In:
{prompt_trace}

    
Out:
{prompt_example}
>>>

This is the input trace, transform it all:
<<<
{target_trace}
>>>
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


    list_of_prompts = [
        clean_state_goal_plan_v4a_1, 
        clean_state_goal_plan_v4b_1, 
        clean_state_goal_plan_v4c_1, 
        clean_state_goal_plan_v4d_1, 
        clean_state_goal_plan_v4e_1, 
        clean_state_goal_plan_v4f_1, 
        clean_state_goal_plan_v4g_1, 
        clean_state_goal_plan_v4h_1, 
        clean_state_goal_plan_v4i_1
    ]

    types_of_envs = ["clean","cool","examine", "heat", "put", "puttwo"]
    # save_folder = "playgrounds"
    # base_variable_name = "state_goal_plan_v4"
    # file_name = "alfworld_prompts_utils_v4_{env_type}.py"


    react_prompt_file = "playgrounds/alfworld_react_prompts_original_v3.json"
    with open(react_prompt_file, "r") as file:
        original_prompts = json.load(file)

    env_type = types_of_envs[4]
    # env_type = "cool"


    prompt_trace = original_prompts["act_examine_1"]
    target_trace = original_prompts[f"act_{env_type}_2"]



    # example_prompt = clean_state_goal_plan_v4i_1
    example_prompt = generate_string_prompt(examine_v4_base)
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
# 2. `}\n\n` with `}""",\n"""`

# Replace (v2):
# 1. `\n\n{` with `""",\n"""{`
# 2. `}\n\n` with `}""",\n"""`
 
