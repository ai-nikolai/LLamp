import yaml
import csv
import os
import json
import re
import argparse
from datetime import datetime

import cohere

from llamp.llms.human import Human
from llamp.llms.api import (
    AnthropicChat, AnthropicText,
    CohereChat, CohereChatText, CohereText,
    OpenAIChat, OpenAIChatText, OpenAIText, OpenAIChatTextSampling,
    NvidiaChatText,
    CerebrasChatText
)


# import alfworld
# import alfworld.agents.environment

import alfworld.agents.environment as environment
# import alfworld.agents.modules.generic as generic

def build_arg_parser():
    """ Returns the argument parser"""
    parser = argparse.ArgumentParser(description="Alfworld Env with various agents")
    parser.add_argument(
        "--agent",
        type=str,
        default="ours",
        choices=[
            "react",
            "jsonreact",
            "agentbench",
            "ours",
            "ours-text"
        ],
        help="The Agent / Method choice.",
    )

    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-0125", help="Underlying Model to use.(Needs to align with agent, otherwise default model will be used.)")
    parser.add_argument(
        "--llm_type",
        type=str,
        default="OpenAIChatTextSampling",
        choices=[
            "AnthropicChat",
            "CohereChat" ,
            "OpenAIChat" ,
            "AnthropicText" ,
            "CohereText" ,
            "OpenAIText" ,
            "CohereChatText",
            "OpenAIChatText" ,
            "OpenAIChatTextSampling",
            "NvidiaChatText",
            "CerebrasChatText"
        ],
        help="The type of llamp.llms to use.",
    )

    parser.add_argument("--agent_version", type=int, default=1, help="Method Version (if applicable)")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature")
    parser.add_argument("--num_prompts", type=int, default=2, help="Number of prompts to use (if applicable) (LEGACY)")

    parser.add_argument("--prompt_ids", nargs='+', type=int, default=[1,0], help="A list of prompt indices to use, e.g. --prompt_indices 0 1")

    # Keys for our method
    parser.add_argument("--keys_to_remove", type=str, default="[]",help="DEPRACTED => Doesn't Work anymore. Needs to be json.loads-able list of keys to remove (LEGACY).")
    parser.add_argument("--keys_to_use", type=str, help="Needs to be json.loads-able list of keys to use")
    parser.add_argument("--keys_renaming", type=str, help="Needs to be json.loads-able list of new key names.")

    # RUN / ENV:
    parser.add_argument("--trial_name", type=str, default="v3_0_eval_test", help="Underlying Model to use.(Needs to align with agent, otherwise default model will be used.)")
    parser.add_argument("--start_index", type=int, default=0, help="Starting Index to use (inclusive).")
    parser.add_argument("--end_index", type=int, default=0, help="Ending index to use (inclusive). (Overrides num_envs)")
    parser.add_argument("--num_envs", type=int,  default=1, help="Sets the num of envs to run (gets overriden by end index)")


    parser.add_argument(
        "--eval_split",
        type=str,
        default="eval_out_of_distribution",
        choices=[
            "eval_out_of_distribution",
            "eval_in_distribution"
        ],
        help="The alfworld split to use.",
    )
    parser.add_argument("--apply_correction", action="store_true", default=False, help="Whether to apply the 'Put Regex' correction")
    parser.add_argument("--resample", action="store_true", default=False, help="Whether to resample on repetition")
    parser.add_argument("--resample_temperature", type=float, default=0.1, help="Resample Temperature increase.")

    parser.add_argument("--force_run", action="store_true", default=False, help="Whether to apply the 'Put Regex' correction")

    parser.add_argument("--silent", action="store_true", default=False, help="Whether to suppress messages during the game loop.")

    return parser




if __name__ =="__main__":
    # from playground_alfworld_ablation_generator import return_jsonstate_prompt, return_stringstate_prompt
    # from playground_alfworld_react_prompt_utils import return_react_examples, return_agentbench_prompts, return_json_react_examples

    print("Import successful.")

    # from playground_alfworld_ablation_generator import return_jsonstate_prompt, return_stringstate_prompt
    # from playground_alfworld_react_prompt_utils import return_react_examples, return_agentbench_prompts, return_json_react_examples

    temperature=0.0
    model="llama3.1-8b"
    agent = CerebrasChatText(temperature=temperature, model=model)

    # response = agent.act("Hi, how are you?", return_token_count=True)
    # print(response)

    parser = build_arg_parser()
    args = parser.parse_args()

    print(args)

    # NEW STUFF
    split = args.eval_split
    print("Split Extracted successfully.")
    # split = "eval_in_distribution"
    # load config

    try:
        print("Trying to load config.")
        with open('./base_config.yaml') as reader:
            config = yaml.safe_load(reader)
    except Exception as e:
        print(e)
    print("Config loaded successfully.")

    env_type = config['env']['type'] # 'AlfredTWEnv' or 'AlfredThorEnv' or 'AlfredHybrid'
    print("Env Type set successfully")
    # setup environment
    env = getattr(environment, env_type)(config, train_eval=split)
    print("Got Env successfully.")

    env = env.init_env(batch_size=1)
    print("Init Env successfully.")

    print("Test Succeeded!")
