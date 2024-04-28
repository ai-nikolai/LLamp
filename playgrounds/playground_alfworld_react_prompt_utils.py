import json
import os

BASE_FOLDER = "prompts"

# react_prompt_file_name = "alfworld_react_prompts_original_v3.json"
react_prompt_file_name = "alfworld_react_prompts_original_v3_corrected.json"
react_prompt_file = os.path.join("playgrounds",BASE_FOLDER, react_prompt_file_name)
with open(react_prompt_file, "r") as file:
    original_react_prompts = json.load(file)



agentbench_prompt_file_name = "agentbench_prompts_v1_plan_first.json"
agentbench_prompt_file = os.path.join("playgrounds",BASE_FOLDER,agentbench_prompt_file_name)
with open(agentbench_prompt_file, "r") as file:
    original_agentbench_prompts_v1 = json.load(file)

agentbench_prompt_file_name = "agentbench_prompts_v2_react.json"
agentbench_prompt_file = os.path.join("playgrounds",BASE_FOLDER,agentbench_prompt_file_name)
with open(agentbench_prompt_file, "r") as file:
    original_agentbench_prompts_v2 = json.load(file)


def return_react_examples(env_type, num=2, swap=False, first_id=0, second_id=1):
    """Given the env type return a react example."""
    if swap:
        first_index = second_id
        second_index = first_id
    else:
        first_index = first_id
        second_index = second_id
    target_trace = ""
    if num == 2:
        target_trace1 = original_react_prompts[f"react_{env_type}_{first_index}"]
        target_trace2 = original_react_prompts[f"react_{env_type}_{second_index}"]

        target_trace = target_trace1+ "\n\n" + target_trace2

    elif num==1:
        target_trace = original_react_prompts[f"react_{env_type}_{first_index}"]

    return target_trace


def extract_command_and_format(command, version=1, think_key="think", action_key="action"):
    """Sub func to extract commands.
    Documentation on double {{, }} for f-strings 
    https://stackoverflow.com/questions/5466451/how-do-i-escape-curly-brace-characters-in-a-string-while-using-format-or
    """
    thinking = False
    if "think:" in command:
        sys_think = command.split("\n")[0].split("think:")[1].strip()
        sys_act = ""
        thinking = True
    else:
        sys_act = command.split("\n")[0].strip()
        sys_think = ""

    if version==1:
        if thinking:
            sys_response = f'{{\n"{think_key}": "{sys_think}"\n}}' 
        else:
            sys_response = f'{{\n"{action_key}": "{sys_act}"\n}}'

    elif version==2:
        sys_response = f'{{\n"{think_key}": "{sys_think}",\n"{action_key}": "{sys_act}"\n}}' 

    elif version==3:
        if thinking:
            sys_response = f'{{\n"response": "think: {sys_think}"\n}}' 
        else:
            sys_response = f'{{\n"response": "{sys_act}"\n}}'

    env_observation = command.split("\n")[1]

    return sys_response, env_observation


def return_json_react_examples(env_type, num=1, swap=False, first_id=0, second_id=1, version=1, think_key="think", action_key="action", return_list=False):
    """
    Given the env type return a react example.

    """
    target_trace = ""
    if return_list:
        target_trace_list = []

    if swap:
        index_list = [second_id, first_id]
    else:
        index_list = [first_id, second_id]

    for example_idx in range(num):
        if example_idx>0:
            target_trace+="\n\n"
        
        string_trace = original_react_prompts[f"react_{env_type}_{index_list[example_idx]}"]

        commands = string_trace.split(">")

        if return_list:
            # Need to append a list to have one list per example
            target_trace_list.append( [commands[0].strip()] )

        for idx,command in enumerate(commands[1:]):
            sys_response, env_observation = extract_command_and_format(command, version, think_key, action_key)
            commands[idx+1] = sys_response+"\n\n"+env_observation+"\n\n"
            if return_list:
                target_trace_list[example_idx].append(sys_response)
                target_trace_list[example_idx].append(env_observation)

        target_trace += ">".join(commands)

    if return_list:
        return target_trace_list

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


def check_all_json(react_json_list):
    """Assumes obs, sys_response alternating."""
    for idx, obs in enumerate(react_json_list):
        try:
            if idx%2 == 1:
                tmp = json.loads(obs)
        except Exception as e:
            return False, obs, idx, str(e)
    return True, None, None, None

if __name__=="__main__":
    env_type = "puttwo"
    prompt_trace = return_json_react_examples(env_type, num=2, version=1, think_key="think", action_key="action", return_list=False)
    print(prompt_trace)

    env_types = ["clean","cool","examine","heat","put","puttwo"]
    indexs=[0,1,2]
    versions = [1,2,3]
    global_success = True
    for env_type in env_types:
        for index in indexs:
            for version in versions:
                list1 = return_json_react_examples(env_type, num=1, first_id=index, second_id=1, version=version, think_key="think", action_key="action", return_list=True)
                success, example, json_idx, error_message= check_all_json(list1[0])
                if not success:
                    global_success = False
                    print("\n\n===")
                    print(f"FAILED: env:{env_type}, react_num:{index}, json_index:{json_idx}, version:{version}")
                    print("--")
                    print(example)
                    print("--")
                    print(error_message)

    if global_success:
        print("All prompts are correct")

    # print(list1)
    # print(len(list1))

    # EOF