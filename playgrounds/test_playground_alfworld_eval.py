from playground_alfworld_eval import get_prompt_example

if __name__ == "__main__":
    agent_types = ["react", "agentbench", "jsonreact", "ours"]
    prompt_ids = [ [1,0], [0,1], [1,2,0] ]
    versions = [1,2,3]
    env_types = ["clean","cool","examine","heat","put","puttwo"]
    keys_to_use = ["goal","thought","plan","action"]

    prompt_id_strings = [ "1_0", "0_1", "1_2_0"]
    version_strings = ["v1","v2","v3"]
    keys_to_use_string = "k-goal_thought_plan_action"


    error_flag = False
    for env_type in env_types:
        for pidx, prompt_id in enumerate(prompt_ids):
            for agent_type in agent_types:
                    for vidx, version in enumerate(versions):
                        if agent_type == "agentbench" and version==3:
                            continue

                        prompt_name,_,_,_ = get_prompt_example(agent_type, env_type, prompt_ids=prompt_id, version=version, generate_prompt=True, keys_to_use=keys_to_use)

                        if agent_type == "ours":
                            desired_prompt_name = f"jsonstate-{prompt_id_strings[pidx]}-{keys_to_use_string}"

                        if agent_type == "react":
                            desired_prompt_name = f"react-{prompt_id_strings[pidx]}"

                        if agent_type == "jsonreact":
                            desired_prompt_name = f"jsonreact-{prompt_id_strings[pidx]}-{version_strings[vidx]}"

                        if agent_type == "agentbench":
                            desired_prompt_name = f"agentbench-{version_strings[vidx]}"
                        
                        try:
                            assert prompt_name==desired_prompt_name, f"\n\n==\nPrompt names are not the same::\ndesired:{desired_prompt_name},\nactual:{prompt_name} \nagent:{agent_type}, \nversion:{version}, \nenv_type:{env_type}, \nprompt_id:{prompt_id}" 
                        except AssertionError as e:
                            print(e)
                            error_flag = True

                        # print(prompt_name)

    if error_flag:
        print("FAIL - prompt names are not behaving as expected.")
    else:
        print("SUCCESS - all prompt names match desired prompt names.")

    # prompt_name,_,_,_ = get_prompt_example("agentbench", "clean", prompt_ids=[1,0], version=0, generate_prompt=True)
    # print(prompt_name)