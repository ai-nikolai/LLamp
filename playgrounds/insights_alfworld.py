import pandas as pd
import json
import os
import re

import seaborn as sns
import matplotlib.pyplot as plt

# Assuming your DataFrame is named df
# Example:
# df = pd.DataFrame({
#     'num_of_steps': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#     'success': [True, False, True, False, True, False, True, False, True, False]
# })


GPT_MODEL_OF_INTEREST="gpt-3.5-turbo-1106"

# Create the box plot
def add_clean_prompt_names(df):
    """ Adds clean prompt names."""
    # Define a function to rename categories based on rules
    def rename_prompt(prompt_name):
        out_prompt_name = prompt_name
        out_prompt_name=out_prompt_name.replace("-1_0",": ")
        out_prompt_name=out_prompt_name.replace("-k-","")
        out_prompt_name=out_prompt_name.replace("current_location+current_inventory","state")
        out_prompt_name=out_prompt_name.replace("action","action)")        
        out_prompt_name=out_prompt_name.replace("react: ","ReAct (thought + action)")
        out_prompt_name=out_prompt_name.replace("stringstate: ","StateAct (")

        return out_prompt_name

    # Apply the function to the 'category' column
    df['prompt_name_clean'] = df['prompt_name'].apply(rename_prompt)



def plot_three(type, data1, data2, data3, desc1, desc2, desc3, title, prompt_name = "prompt_name_clean"):
    """ """
    # Create a figure with 3 subplots (1 row, 3 columns)
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    # #################### GOAL RELATED
    if type =="goal":
        co1 = [
        "stringstate: state+thought+action", 
        "stringstate: goal+state+thought+action"]
        co2 = [
        "stringstate: state+action",
        "stringstate: goal+state+action"]
        co3=[
        "react: thought+action, alternating",
        "stringstate: goal+thought+action"]


    # #################### Other Related
    else:
        co1 = [
        "stringstate: goal+thought+action",
        "stringstate: goal+state+thought+action"]
        co2 = [
        "stringstate: goal+state+action",
        "stringstate: goal+state+thought+action"]
        co3=[
        "jsonstate: goal+state+thought+action",
        "stringstate: goal+state+thought+action"]
    
    hue_order = [
     "react: thought+action, alternating"
    ]

    # Line plot
    sns.barplot(x='num_of_steps_bucket', y='score', hue=prompt_name, hue_order=co1, data=data1, ax=axs[0])
    axs[0].set_title(f'Average Score by Number of Steps - {desc1}')
    axs[0].set_xlabel('Number of Steps')
    axs[0].set_ylabel('Average Score')

    # Scatter plot
    sns.barplot(x='num_of_steps_bucket', y='score', hue=prompt_name, hue_order=co2, data=data2, ax=axs[1])
    axs[1].set_title(f'Average Score by Number of Steps - {desc2}')
    axs[1].set_xlabel('Number of Steps')
    axs[1].set_ylabel('Average Score')

    # Bar plot
    sns.barplot(x='num_of_steps_bucket', y='score', hue=prompt_name, hue_order=co3, data=data3, ax=axs[2])
    axs[2].set_title(f'Average Score by Number of Steps - {desc3}')
    axs[2].set_xlabel('Number of Steps')
    axs[2].set_ylabel('Average Score')

    fig.suptitle(title, fontsize=16)


    # Display the plots
    plt.tight_layout()
    plt.show()


def get_average_scores(df, bucket_size=10, key="num_of_steps", prompt_name = "prompt_name_clean"):
    """computes the average scores."""
    df['score'] = df['success'].astype(int)
    df['num_of_steps_bucket'] = pd.cut(df[key], bins=range(0, df[key].max() + bucket_size, bucket_size), right=False)

    # Calculate the average score for each num_of_steps
    average_scores = df.groupby(['num_of_steps_bucket', prompt_name])['score'].mean().reset_index()
    
    return  average_scores   


def plot_avg(df, bucket_size=10, key="num_of_steps"):
    average_scores = get_average_scores(df, bucket_size=bucket_size, key=key)

    # Create the plot
    sns.barplot(x='num_of_steps_bucket', y='score', hue="prompt_name", data=average_scores)

    # Set the labels and title
    plt.xlabel('Number of Steps')
    plt.ylabel('Average Score')
    plt.title('Average Score by Number of Steps')

    # Show the plot
    plt.show()


def plot_avg_line(df):
    df['score'] = df['success'].astype(int)
    # df['num_of_steps_bucket'] = pd.cut(df['num_of_steps'], bins=range(0, df['num_of_steps'].max() + bucket_size, bucket_size), right=False)

    # Calculate the average score for each num_of_steps
    average_scores = df.groupby(['num_of_steps', 'prompt_name'])['score'].mean().reset_index()

    # Create the plot
    sns.scatterplot(x='num_of_steps', y='score', hue="prompt_name", data=average_scores)

    # Set the labels and title
    plt.xlabel('Number of Steps')
    plt.ylabel('Average Score')
    plt.title('Average Score by Number of Steps')

    # Show the plot
    plt.show()


def plot_bar(df2):
    sns.boxplot(x='success', y='num_of_steps', hue="prompt_name",data=df2)

    # Set the labels and title
    plt.xlabel('Success')
    plt.ylabel('Number of Steps')
    plt.title('Number of Steps by Success')

    # Show the plot
    plt.show()


def get_df_for_goal_comp_full(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2

def get_df_for_goal_comp_nothought(df):
    df2 = df[  
    (
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action")
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2


def get_df_for_goal_comp_react(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action")
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        (df["prompt_name"]=="stringstate-1_0-k-goal+thought+action") |
        (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2



def get_df_for_state_comp_full(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2

def get_df_for_state_comp_nothought(df):
    df2 = df[  
    (
        (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action")
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2


def get_df_for_thought_comp_full(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2

def get_df_for_thought_comp_nostate(df):
    df2 = df[  
    (
        (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+thought+action")
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2

def get_df_for_thought_comp_nogoal(df):
    df2 = df[  
    (
        (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2


def get_df_for_json_comp_full(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        (df["prompt_name"]=="jsonstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") 
        # (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2


def get_df_states(df):
    df2 = df[  
    (
        # (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+action") |
        # (df["prompt_name"]=="jsonstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-goal+action") |
        # (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+thought+action") |
        (df["prompt_name"]=="stringstate-1_0-k-current_location+current_inventory+thought+action") |
        (df["prompt_name"]=="stringstate-1_0-k-goal+current_location+current_inventory+thought+action") |
        (df["prompt_name"]=="react-1_0") 
    ) & 
    (df["model"]==GPT_MODEL_OF_INTEREST) 
    ]
    return df2




def extract_react_command_and_arguments(action_string):
    """ 
    Extracts the react command and arguments 
    
    WARNGING: 
        At the moment:
        Only extract commands that change the state, otherwise returns None.

    Regex Builder: https://regex101.com/r/BK3La8/1
    """
    # State changing regex expressions.
    put_regex = """put\s(\w+(?:\s\w+)?\s\d+)\sin\/on\s(\w+(?:\s\w+)?\s\d+)"""
    goto_regex = """go\sto\s(\w+(?:\s\w+)?\s\d+)"""
    take_regex = """take\s(\w+(?:\s\w+)?\s\d+)\sfrom\s(\w+(?:\s\w+)?\s\d+)"""
    
    # #Commands that do not change the state
    # TODO they need to be update to extract arguments correctly.
    # open_regex = """open(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""    
    # cool_regex = """cool(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # clean_regex = """clean(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # use_regex = """use(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # heat_regex = """heat(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # examine_regex = """examine(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # close_regex = """close(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    # look_regex = """look"""

    # changing_regexes = [put_regex, goto_regex, take_regex]

    answer = re.match(put_regex,action_string)
    if answer: #Put case
        put_object = answer.group(1)
        put_place = answer.group(2)
        return "put", put_object, put_place

    answer = re.match(goto_regex,action_string)
    if answer: #Put case
        goto_place = answer.group(1)
        return "goto", goto_place, None  

    answer = re.match(take_regex,action_string)
    if answer: #Put case
        take_object = answer.group(1)
        take_place = answer.group(2)
        return "take", take_object, take_place

    # Otherwise return nothing (as it's not changing the state)
    return None, None, None

def update_reference_state_with_action(reference_state, action_string):
    """ Update the reference state with a given command. """
    command, arg1, arg2 = extract_react_command_and_arguments(action_string)

    if command == "goto":
        reference_state["current_location"] = arg1
        reference_state["locations_visited"].append(arg1)
    
    if command == "put":
        # TODO check one actually carries this object.
        reference_state["current_inventory"] = ""

    if command == "take":
        # TODO check one can actually take this object. (harder)
        reference_state["current_inventory"] = arg1




def update_states(df):
    # Applying the update_steps function to the relevant rows
    df['correct_states'] = df.apply(
        lambda row: count_correct_states(row['trace_file'], row["keys_to_use"]) if "stringstate-" in row['prompt_name'] else 0,
        axis=1
    )
    df['valid_states'] = df.apply(
        lambda row: count_valid_states(row['trace_file'], row["keys_to_use"]) if "stringstate-" in row['prompt_name'] else row['num_of_steps'],
        axis=1
    )
    df["next_correct_states"] = df.apply(
        lambda row: count_correct_states2(row['trace_file'], row["keys_to_use"]) if "stringstate-" in row['prompt_name'] else 0,
        axis=1
    )
    return df


def count_valid_states(filename, keys_to_use):
    keys_to_use = eval(keys_to_use)
    normalise_by = len(keys_to_use)

    with open(filename) as file:
        data = json.load(file)
    count = 0

    for idx,content in enumerate(data):
        temp_count = 0
        if content["role"] == "assistant":
            llm_output = content["content"]
           
            if "current_location" in keys_to_use:
                SEP2 = "current location: " 
                if SEP2 in llm_output:
                    temp_count += 1

            if "current_inventory" in keys_to_use:
                SEP3 = "current inventory: " 
                if SEP3 in llm_output:
                    temp_count += 1

            if "thought" in keys_to_use:
                SEP3 = "thought: " 
                if SEP3 in llm_output:
                    temp_count += 1

            if "action" in keys_to_use:
                SEP3 = "action: " 
                if SEP3 in llm_output:
                    temp_count += 1

            if "goal" in keys_to_use:
                SEP3 = "goal: " 
                if SEP3 in llm_output:
                    temp_count += 1

            # if temp_count > 0 and temp_count<normalise_by:
            #     print(llm_output)
            #     print(keys_to_use)
            #     print(temp_count)
            #     print(normalise_by)

            #     input()

            count += temp_count / normalise_by

    return count

def count_correct_states(filename, keys_to_use):
    """Counts how many non-thought actions"""
    keys_to_use = eval(keys_to_use)
    normalise_by = 0

    if "current_location" in keys_to_use:
        normalise_by += 1

    if "current_inventory" in keys_to_use:
        normalise_by += 1

    if normalise_by == 0:
        normalise_by = 1


    with open(filename) as file:
        data = json.load(file)
    count = 0
    reference_state = {
        "locations_visited":[],
        "current_location": "starting location",
        "current_inventory": ""
    }
    for idx,content in enumerate(data):
        temp_count = 0
        curr_loc = False
        curr_inv = False
        if content["role"] == "assistant":
            llm_output = content["content"]
            if idx<len(data)-1:
                if data[idx+1]["content"]=="Nothing happens.\n":
                    # print(f"Nothing:{idx}")
                    # skip when nothing happens
                    continue

            if "current_location" in keys_to_use:
                SEP2 = "current location: " 
                if SEP2 in llm_output:
                    if llm_output.split(SEP2)[-1].startswith(reference_state["current_location"]):
                        temp_count += 1
                    else:
                        # print(filename)
                        # print(idx)
                        # print(f"---data:{idx}")
                        # print(data[idx-2]["content"])
                        # print(data[idx-1]["content"])
                        # print(data[idx]["content"])
                        # print("---llm:")
                        # print(llm_output)
                        # print(llm_output.split(SEP2)[-1])

                        # print("---state:")
                        # print(reference_state)

                        # print("previous command:")
                        # actual_command = data[idx-2]["content"].split("action:")[-1].strip()
                        # print(actual_command)
                        # print(extract_react_command_and_arguments(actual_command))

                        # update the reference state with correct thing for the next state tracking.
                        correct_value = llm_output.split(SEP2)[-1].split('\n')[0]
                        reference_state["current_location"] = correct_value
                        
                        # print(f"correct:{correct_value}")
                        # print("---state after:")
                        # print(reference_state)
                        # input()

            if "current_inventory" in keys_to_use:
                SEP3 = "current inventory: " 
                if SEP3 in llm_output:
                    if llm_output.split(SEP3)[-1].startswith(reference_state["current_inventory"]):
                        temp_count += 1
                    else:
                        # update the reference state with correct thing for the next state tracking.
                        correct_value = llm_output.split(SEP3)[-1].split('\n')[0]
                        reference_state["current_inventory"] = correct_value
                    # else:
                        # print(filename)
                        # print(idx)
                        # print(f"---data:{idx}")
                        # print(data[idx-2]["content"])
                        # print(data[idx-1]["content"])
                        # print(data[idx]["content"])
                        # print("---llm:")
                        # print(llm_output)
                        # print(llm_output.split(SEP2)[-1])

                        # print("---state:")
                        # print(reference_state)

                        # print("previous command:")
                        # actual_command = data[idx-2]["content"].split("action:")[-1].strip()
                        # print(actual_command)
                        # print(extract_react_command_and_arguments(actual_command))

                        # update the reference state with correct thing for the next state tracking.
                        correct_value = llm_output.split(SEP2)[-1].split('\n')[0]
                        reference_state["current_inventory"] = correct_value
                        

                        # print(f"correct:{correct_value}")
                        # print("---state after:")
                        # print(reference_state)

                        # input()

            SEP = "action:"
            if SEP in llm_output:
                # print(f"=================START{idx}")
                # print(reference_state)
                actual_action = llm_output.split(SEP)[-1].strip()
                update_reference_state_with_action(reference_state,actual_action)
                # print(actual_action)
                # print(reference_state)
                # print("=================END")
        
            count += temp_count / normalise_by


    return count



def count_correct_states2(filename, keys_to_use):
    """Counts how many non-thought actions"""
    keys_to_use = eval(keys_to_use)
    normalise_by = 0

    if "current_location" in keys_to_use:
        normalise_by += 1

    if "current_inventory" in keys_to_use:
        normalise_by += 1

    if normalise_by == 0:
        normalise_by = 1


    with open(filename) as file:
        data = json.load(file)
    count = 0
    valid_count = 0
    
    SEP2 = "current location: " 
    SEP3 = "current inventory: " 
    SEP = "action:"

    for idx,content in enumerate(data):
        reference_state = {
            "locations_visited":[],
            "current_location": "starting location",
            "current_inventory": ""
        }
        temp_count = 0
        curr_loc = False
        curr_inv = False

        if not (("current_location" in keys_to_use) and ("current_inventory" in keys_to_use)):
            continue

        if content["role"] == "assistant":
            llm_output = content["content"]
            print(llm_output)
            print(SEP2 in llm_output)
            print(SEP3 in llm_output)
            if idx<len(data)-1:
                if data[idx+1]["content"]=="Nothing happens.\n":
                    # print(f"Nothing:{idx}")
                    # skip when nothing happens
                    continue

                if (SEP2 in llm_output) and (SEP3 in llm_output):
                    valid_count += 1
                else:
                    continue

                # main action
                actual_action = llm_output.split(SEP)[-1].strip()

                # Current Location
                current_value = llm_output.split(SEP2)[-1].split('\n')[0]
                reference_state["current_location"] = current_value                

                # Current Inventory
                current_value = llm_output.split(SEP3)[-1].split('\n')[0]
                reference_state["current_inventory"] = current_value 

                # The idea here is to create a state from the current turn and check if in the next turn tracked it correctly given the current one.
                update_reference_state_with_action(reference_state,actual_action)

                if data[idx+2]["content"].split(SEP2)[-1].startswith(reference_state["current_location"]):
                    temp_count += 1
                if data[idx+2]["content"].split(SEP3)[-1].startswith(reference_state["current_location"]):
                    temp_count += 1
        

            count += temp_count / normalise_by

    if valid_count == 0:
        valid_count = 1
    return count / valid_count



def update_steps(df):
    # Applying the update_steps function to the relevant rows
    df['num_of_steps_updated'] = df.apply(
        lambda row: count_steps(row['trace_file']) if row['prompt_name'] == 'react-1_0' else row['num_of_steps'],
        axis=1
    )
    return df

def count_steps(file_name):
    """Counts how many non-thought actions"""
    with open(file_name) as file:
        data = json.load(file)
    count = 0
    for idx,content in enumerate(data):
        if content["role"] == "assistant":
            if content["content"].startswith(">think") or content["content"].startswith("> think"):
                continue
            else:
                count+=1
    return count



if __name__=="__main__":
    trial_name = "v4_1_2_eval"
    CORRECTION_STRING = "No Corrections"



    # trial_name = "v4_1_2_eval_correction"
    # CORRECTION_STRING = "Corrections"


    base_path = os.path.join("game_logs",f"alfworld_eval_{trial_name}")
    file_path = os.path.join(base_path,"alfworld_results.csv")
    

    df = pd.read_csv(file_path)
    update_steps(df)
    update_states(df)
    add_clean_prompt_names(df)


    ################
    # PLOTTING Successful vs. Valid vs. non-valid states.
    # print(df.columns)
    df["successful_state_tracking"] = df["correct_states"]/df["num_of_steps"]
    df["successful_state_tracking_2"] = df["correct_states"]/df["valid_states"]
    df["valid_states_percentage"] = df["valid_states"]/df["num_of_steps"]
    df["successful_next_states_tracking"] = df["next_correct_states"]/df["num_of_steps"]

    # what_to_plot = "next_correct_states"
    what_to_plot = 'successful_state_tracking'
    # what_to_plot = 'successful_state_tracking_2'
    # # # what_to_plot = 'correct_states'
    # # # what_to_plot = 'valid_states'
    # # # what_to_plot = 'valid_states_percentage'
    # what_to_plot = "successful_next_states_tracking"
    # what_to_plot = "next_correct_states"
    # what_to_plot = "num_of_steps"
    # what_to_plot = "success"

    # average_scores = df.groupby(['prompt_name'])["successful_state_tracking"].mean().reset_index()
    # average_scores["successful_state_from_valid"] = df.groupby(['prompt_name'])["successful_state_tracking_2"].mean().reset_index()["successful_state_tracking_2"]
    # average_scores["valid_states_percentage"] = df.groupby(['prompt_name'])["valid_states_percentage"].mean().reset_index()["valid_states_percentage"]

    # hue_order = [
    #     "react-1_0",
    #     "stringstate-1_0-k-goal+thought+action",
    #     "stringstate-1_0-k-current_location+current_inventory+thought+action",
    #     "stringstate-1_0-k-goal+current_location+current_inventory+thought+action"
    # ]

    hue_order = [
        "ReAct (thought + action)",
        "StateAct (goal+thought+action)",
        "StateAct (state+thought+action)",
        "StateAct (goal+state+thought+action)",
    ]

    # df00 = get_df_states(df)
    # average_scores = get_average_scores(df00, bucket_size=10, key="num_of_steps_updated")
    # x = sns.barplot(x="num_of_steps_bucket",y="score", hue="prompt_name_clean", hue_order=hue_order,data=average_scores)
    # plt.legend(title="")
    # x.set_ylabel('')
    # x.set_xlabel('Number of Steps')
    # plt.title("Average Success Rate vs. Number of Steps")

    
    average_scores = df.groupby(['prompt_name'])[what_to_plot].mean().reset_index()
    average_scores.to_csv(f"states_count_{CORRECTION_STRING}.csv", sep='&', float_format='%.4f', index=False)
    sns.barplot(y=what_to_plot, hue="prompt_name", data=average_scores)

    plt.show()
    input()
    ################
    print(df.columns)

    df["avg_out_tokens_per_step"] = df["total_out_token_accumulated"]/df["num_of_steps"]
    
    token_count = df.groupby(['prompt_name','model'])["total_in_token_accumulated"].sum().reset_index()
    token_count["total_out_token_accumulated"] = df.groupby(['prompt_name','model'])["total_out_token_accumulated"].sum().reset_index()["total_out_token_accumulated"]
    token_count["average_out_token"] = df.groupby(['prompt_name','model'])["avg_out_tokens_per_step"].mean().reset_index()["avg_out_tokens_per_step"]

    
    token_count.to_csv(f"token_count_{CORRECTION_STRING}.csv", sep='&', float_format='%.4f', index=False)

    input(">>>")



    # print(df["prompt_name"]=="react-1_0")
    # df2 = df[ (df["prompt_name"]=="react-1_0") & (df["model"]==GPT_MODEL_OF_INTEREST) ]
    # df2 = df[ (df["model"]==GPT_MODEL_OF_INTEREST) ]


    ################
    # PLOTTING Goal vs. no-goal performance.
    df1 = get_df_for_goal_comp_full(df)
    # # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")


    df2 = get_df_for_goal_comp_nothought(df)
    # # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")


    df3 = get_df_for_goal_comp_react(df)
    # # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")
    
    as1 = get_average_scores(df1, bucket_size=10, key="num_of_steps_updated")
    as2 = get_average_scores(df2, bucket_size=10, key="num_of_steps_updated")
    as3 = get_average_scores(df3, bucket_size=10, key="num_of_steps_updated")

    plot_three("goal",as1,as2, as3, "State, Thought, Action", "State, Action", "Thought Action", f"Ablation - {CORRECTION_STRING} - Goal vs. No-Goal")
    ################
    ################
    # PLOTTING State vs. no state
    df1 = get_df_for_state_comp_full(df)
    # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")

    # df2 = get_df_for_state_comp_nothought(df)
    # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")
    

    ################
    # PLOTTING Thought vs. no-thought performance.
    df2 = get_df_for_thought_comp_full(df)
    # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")

    # df2 = get_df_for_thought_comp_nostate(df)
    # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")

    # df2 = get_df_for_thought_comp_nogoal(df)
    # plot_avg(df2,bucket_size=10, key="num_of_steps_updated")


    # JSON
    df3 = get_df_for_json_comp_full(df)

    as1 = get_average_scores(df1, bucket_size=10, key="num_of_steps_updated")
    as2 = get_average_scores(df2, bucket_size=10, key="num_of_steps_updated")
    as3 = get_average_scores(df3, bucket_size=10, key="num_of_steps_updated")

    plot_three("other",as1,as2, as3, "No State vs. State", "No Thought vs. Thought", "Json vs. No-Json", f"Ablations - {CORRECTION_STRING} - State, Thought, Json")

# (df["prompt_name"]=="stringstate-1_0-k-goal-current_location-current_inventory-action") &
    # print(df)
    # print(df2)
    # print(df2.columns)
    # print(df2["success"])

    # df2.hist(column=["success","num_of_steps"])
    # df2.plot(y="num_of_steps",kind="hist", by="success")
    # plt.show()



