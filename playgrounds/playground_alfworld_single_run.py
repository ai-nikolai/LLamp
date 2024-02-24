import alfworld
import alfworld.agents.environment
import yaml

from llamp.cohere_agent import CohereAgent
from llamp.openai_agent import OpenAIAgent

def process_ob(ob):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ')+2:]

    if ob == "Nothing happens.":
        ob = "Invalid or Impossible Action. Try again." 
    return ob


PREFIXES = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
}

from alfworld_prompts_utils import clean_simple_goal_plan_1, \
cool_simple_goal_plan_1, \
examine_simple_goal_plan_1, \
heat_simple_goal_plan_1, \
clean_state_goal_plan_1, \
clean_state_goal_plan_v2_1, \
clean_state_goal_plan_v3_1#, \
# clean_state_goal_plan_v4_1, \
# clean_state_goal_plan_v4b_1, \
# clean_state_goal_plan_v4c_1, \
# clean_state_goal_plan_v4d_1, \
# clean_state_goal_plan_v4e_1, \
# clean_state_goal_plan_v4f_1, \
# clean_state_goal_plan_v4g_1, \
# clean_state_goal_plan_v4h_1

from alfworld_prompts_utils_v4_clean import \
clean_state_goal_plan_v4a_1, \
clean_state_goal_plan_v4b_1, \
clean_state_goal_plan_v4c_1, \
clean_state_goal_plan_v4d_1, \
clean_state_goal_plan_v4e_1, \
clean_state_goal_plan_v4f_1, \
clean_state_goal_plan_v4g_1, \
clean_state_goal_plan_v4h_1


PROMPT = [{
            "role" : "system",
            "content" : f"""
You will interact with the environment to solve the given task.

This is the list of all valid actions that you can use:
<<<
- go to <dir> [example: go to table 1]
- open <obj> [example: open door 1]
- close <obj> [example: close door 1]
- put <obj> in/on <obj> [example: put apple 1 in/on table 1]
- take <obj> from <obj> [example: take apple 1 from table 1]
- cool <obj> with <obj> [example: cool apple 1 with fridge 1]
- heat <obj> with <obj> [example: heat apple 1 with fire 1]
- use <obj> [example: use desklamp 1]
>>>


For example:
<<<
{clean_state_goal_plan_v4g_1}
>>>

A few hints:
<<<
If "Nothing happens." or "Invalid Command", then try a valid action that you have not tried before.
Some actions can be only executed in specific places, such as cleaning, heating, cooling...
Learn from the example.
Generate a JSON output.
>>>
"""
        }]

# Stick to the plan.
# Be very precise, especially with respect to locations and objects. For example an apple does not count for a banana.



env_index = 3
agent_index = 1

if agent_index == 1:
    agent = CohereAgent()
elif agent_index==2:
    agent = OpenAIAgent()

agent.update_save_path("game_logs/alfworld_eval_1")
agent.set_base_prompt_and_reset(PROMPT)


if __name__=="__main__":
    with open('playgrounds/base_config.yaml') as reader:
        config = yaml.safe_load(reader)
    split = "eval_out_of_distribution"

    env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
    env = env.init_env(batch_size=1)

    for _ in range(env_index):
        observation, info = env.reset()

    observation = '\n'.join(observation[0].split('\n\n')[1:])
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
    
    print(observation)
    # print(info)
    # print(name)

    game_running_flag = True
    counter = 0
    LIMIT = 20
    try:
        while game_running_flag:
            # action = input(">")
            action = agent.act("Input:\n"+observation)
            print("<<< ACTION >>>:"+action)
            if action.startswith("think:"):
                observation = "You are thinking. Please take an action."
                continue
            if action.startswith('think("'):
                observation = "You are thinking."
                continue
            if 'action("' in action:
                actions = action.split('action("')
                action = actions[1].split('")')[0]
                print(f"Extracted Action:{action}")

            if ('"action" : "' in action):
                actions = action.split('"action" : "')
                action = actions[1].split('"')[0]
                print(f"Extracted Action:{action}")

            if ('"action": "' in action):
                actions = action.split('"action": "')
                action = actions[1].split('"')[0]
                print(f"Extracted Action:{action}")

            if ('"action":"' in action):
                actions = action.split('"action":"')
                action = actions[1].split('"')[0]
                print(f"Extracted Action:{action}")

            observation, reward, done, info = env.step([action])
            # print(observation)

            observation = process_ob(observation[0])
            print("<> OBSERVATION <>:"+observation)
            print(info["won"][0])
            print(done[0])
            if done[0]:
                break
            counter += 1
            if counter == LIMIT:
                break
    finally:
        agent.save()