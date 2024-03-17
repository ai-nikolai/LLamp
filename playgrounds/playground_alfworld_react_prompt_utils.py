import json
import os


react_prompt_file_name = "alfworld_react_prompts_original_v3.json"
react_prompt_file = os.path.join("playgrounds",react_prompt_file_name)
with open(react_prompt_file, "r") as file:
    original_react_prompts = json.load(file)



agentbench_prompt_file_name = "agentbench_prompts.json"
agentbench_prompt_file = os.path.join("playgrounds",agentbench_prompt_file_name)
with open(agentbench_prompt_file, "r") as file:
    original_agentbench_prompts = json.load(file)


def return_react_examples(env_type, num=2):
    """Given the env type return a react example."""
    target_trace = ""
    if num == 2:
        target_trace1 = original_react_prompts[f"react_{env_type}_1"]
        target_trace2 = original_react_prompts[f"react_{env_type}_2"]

        target_trace = target_trace1+ "\n\n" + target_trace2

    elif num==1:
        target_trace = original_react_prompts[f"react_{env_type}_1"]

    return target_trace


def return_agentbench_prompts(env_type, return_base=True):
    """ Returns Agentbench Prompt"""
    prompt_example = "".join(original_agentbench_prompts[env_type])

    if return_base:
        base_prompt = original_agentbench_prompts["base_prompt"]
        return prompt_example, base_prompt
    else:
        return prompt_example

if __name__=="__main__":
    env_type = "clean"
    prompt_trace = return_react_example(env_type)
    print(prompt_trace)