import json
import os


react_prompt_file_name = "alfworld_react_prompts_original_v3.json"
react_prompt_file = os.path.join("playgrounds",react_prompt_file_name)
with open(react_prompt_file, "r") as file:
    original_react_prompts = json.load(file)



agentbench_prompt_file_name = "agentbench_prompts_v1_plan_first.json"
agentbench_prompt_file = os.path.join("playgrounds",agentbench_prompt_file_name)
with open(agentbench_prompt_file, "r") as file:
    original_agentbench_prompts_v1 = json.load(file)

agentbench_prompt_file_name = "agentbench_prompts_v2_react.json"
agentbench_prompt_file = os.path.join("playgrounds",agentbench_prompt_file_name)
with open(agentbench_prompt_file, "r") as file:
    original_agentbench_prompts_v2 = json.load(file)


def return_react_examples(env_type, num=2, swap=False):
    """Given the env type return a react example."""
    if swap:
        first_index = 2
        second_index = 1
    else:
        first_index = 1
        second_index = 2
    target_trace = ""
    if num == 2:
        target_trace1 = original_react_prompts[f"react_{env_type}_{first_index}"]
        target_trace2 = original_react_prompts[f"react_{env_type}_{second_index}"]

        target_trace = target_trace1+ "\n\n" + target_trace2

    elif num==1:
        target_trace = original_react_prompts[f"react_{env_type}_{first_index}"]

    return target_trace


def return_json_react_examples(env_type, num=1):
    """
    Given the env type return a react example.

    TODO: Refactor

    """
    target_trace = ""

    string_trace = original_react_prompts[f"react_{env_type}_1"]

    commands = string_trace.split(">")

    for idx,command in enumerate(commands[1:]):
        if "think:" in command:
            tmp = command.split("\n")[0].split("think:")[1].strip()
            part1 = '{\n"think": "'+tmp+'"\n}' 
        else:
            tmp = command.split("\n")[0].strip()
            part1 = '{\n"action": "'+tmp+'"\n}' 

        part2 = command.split("\n")[1]+"\n"
        commands[idx+1] = part1+"\n"+part2+"\n"

    target_trace = ">".join(commands)

    if num==2:
        string_trace = original_react_prompts[f"react_{env_type}_2"]

        commands = string_trace.split(">")

        for idx,command in enumerate(commands[1:]):
            if "think:" in command:
                tmp = command.split("\n")[0].split("think:")[1].strip()
                part1 = '{\n"think": "'+tmp+'"\n}' 
            else:
                tmp = command.split("\n")[0].strip()
                part1 = '{\n"action": "'+tmp+'"\n}' 

            part2 = command.split("\n")[1]+"\n"
            commands[idx+1] = part1+"\n"+part2+"\n"

        target_trace += "\n\n"+">".join(commands)


    return target_trace


def return_agentbench_prompts(env_type, return_base=True, version=2):
    """ Returns Agentbench Prompt"""
    if version == 1:
        original_agentbench_prompts = original_agentbench_prompts_v1
    elif version == 2:
        original_agentbench_prompts = original_agentbench_prompts_v2
    else:
        raise Exception("Wrong version number for Agentbench prompt")
    
    prompt_example = "".join(original_agentbench_prompts[env_type])
    if return_base:
        base_prompt = original_agentbench_prompts["base_prompt"]
        return prompt_example, base_prompt
    else:
        return prompt_example

if __name__=="__main__":
    env_type = "clean"
    prompt_trace = return_json_react_examples(env_type)
    print(prompt_trace)