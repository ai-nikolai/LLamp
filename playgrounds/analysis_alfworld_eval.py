# import pandas as pd
import os

import csv
import copy



CSV_HEADER = [
        "env_idx", 
        "env_type", 
        "agent_type", 
        "model", 
        "temperature", 
        "success",
        "done",
        "total_reward",
        "num_of_steps", 
        "num_illegal_actions", 
        "num_nothing_happens", 
        "num_repetitions",
        "num_json_dsnt_load",
        "num_multi_json",
        "num_no_json",
        "num_json_and_text",
        "error", 
        "early_stop",
        "keys_removed", 
        "additional_prompt_annotation",
        "trace_file", 
        "prompt_file"
]


IMPORTANT_STATISTICS = [
    "model",
    "temperature", 
    "success", 
    "done", #additional
    "total_reward", #additional
    "num_of_steps", 
    "num_illegal_actions", 
    "num_nothing_happens", 
    "num_repetitions",
    "num_json_dsnt_load",
    "num_multi_json",
    "num_no_json",
    "num_json_and_text",
    "error", 
    "keys_removed"
]


IMPORTANT_STATISTICS = [
    "model",
    "temperature",
    # "env_type",  
    # "env_idx", 
    "success", 
    "done", #additional
    "total_reward", #additional
    "num_of_steps", 
    # "num_illegal_actions", 
    "num_nothing_happens", 
    "num_repetitions",
    # "num_json_dsnt_load",
    # "num_multi_json",
    # "num_no_json",
    # "num_json_and_text",
    "error", 
    "keys_removed",
    "early_stop"
]

def modify_text_prompt(keys_removed):
    """changes to short version"""
    keys = keys_removed.count("+")
    if keys==0:
        return keys_removed
    elif keys>1:
        return "short"
    else:
        return "long"

def extract_correct_stats_from_string_row(tr, im):
    # tr[im["model"]]
    # tr[im["temperature"]]
    if "success" in IMPORTANT_STATISTICS:
        tr[im["success"]] = 1 if tr[im["success"]] == "True" else 0
    if "done" in IMPORTANT_STATISTICS:
        tr[im["done"]] = 1 if tr[im["done"]] == "True" else 0
    if "total_reward" in IMPORTANT_STATISTICS:  
        tr[im["total_reward"]] = float(tr[im["total_reward"]])
    if "num_of_steps" in IMPORTANT_STATISTICS: 
        tr[im["num_of_steps"]] = int(tr[im["num_of_steps"]])
    if "num_illegal_actions" in IMPORTANT_STATISTICS: 
        tr[im["num_illegal_actions"]] = int(tr[im["num_illegal_actions"]])
    if "num_nothing_happens" in IMPORTANT_STATISTICS: 
        tr[im["num_nothing_happens"]] = int(tr[im["num_nothing_happens"]])
    if "num_repetitions" in IMPORTANT_STATISTICS: 
        tr[im["num_repetitions"]] = int(tr[im["num_repetitions"]])
    if "num_json_dsnt_load" in IMPORTANT_STATISTICS: 
        tr[im["num_json_dsnt_load"]] = int(tr[im["num_json_dsnt_load"]])
    if "num_multi_json" in IMPORTANT_STATISTICS: 
        tr[im["num_multi_json"]] = int(tr[im["num_multi_json"]])
    if "num_no_json" in IMPORTANT_STATISTICS: 
        tr[im["num_no_json"]] = int(tr[im["num_no_json"]])
    if "num_json_and_text" in IMPORTANT_STATISTICS: 
        tr[im["num_json_and_text"]] = int(tr[im["num_json_and_text"]])
    if "error" in IMPORTANT_STATISTICS: 
        tr[im["error"]] = 1 if tr[im["error"]] else 0
    if "keys_removed" in IMPORTANT_STATISTICS: 
        tr[im["keys_removed"]] = modify_text_prompt(tr[im["keys_removed"]])
    if "early_stop" in IMPORTANT_STATISTICS: 
        tr[im["early_stop"]] = 1 if tr[im["early_stop"]] else 0
    return tr

def accumulate_two_rows(tr, pr, im):
    # tr[im["model"]]
    # tr[im["temperature"]]

    # tr[im["success"]] += pr[im["success"]]
    # tr[im["done"]] += pr[im["done"]]
    # tr[im["total_reward"]] += pr[im["total_reward"]]
    # tr[im["num_of_steps"]] += pr[im["num_of_steps"]] 
    # tr[im["num_illegal_actions"]] += pr[im["num_illegal_actions"]]
    # tr[im["num_nothing_happens"]] += pr[im["num_nothing_happens"]]
    # tr[im["num_repetitions"]] += pr[im["num_repetitions"]]
    # tr[im["num_json_dsnt_load"]] += pr[im["num_json_dsnt_load"]]
    # tr[im["num_multi_json"]] += pr[im["num_multi_json"]]
    # tr[im["num_no_json"]] += pr[im["num_no_json"]]
    # tr[im["num_json_and_text"]] += pr[im["num_json_and_text"]]
    # tr[im["error"]] += pr[im["error"]]

    for key in IMPORTANT_STATISTICS:
        if not key in ["keys_removed","model","temperature", "env_type"]:
            tr[im[key]] += pr[im[key]]

    # tr[im["keys_removed"]]
    return tr


def get_index_of_important_statistics(header, important_statistics=IMPORTANT_STATISTICS):
    """ finds and returns a list of important indices"""
    out_mapping = {} #for the row
    out_mapping_2 = {}#for the new mapping
    
    for idx,stat in enumerate(important_statistics):
        out_mapping[stat] = header.index(stat)
        out_mapping_2[stat] = idx


    return out_mapping, out_mapping_2



if __name__=="__main__":

    BASE_FOLDER= "game_logs"
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_1" #First big run short/long prompts with chat model using GPT4,3.5 and cohere)
    # CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_react_5" #Run using React prompts using Text model and Cohere and davinci-002
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_react_8" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_react_9" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_new_1" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_clean_v1_test" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_clean_v1_test_react" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_clean_v1_test_agentbench_1" #Run using our prompts with text model using Cohere (for now)
    CURRENT_TRIAL_FOLDER = "alfworld_eval_clean_v1_test_ours"

    # file_signature = "main_clean_react"
    TRIAL_BASE_NAME = "alfworld_eval_"
    file_signature = CURRENT_TRIAL_FOLDER.split(TRIAL_BASE_NAME)[1]


    CURRENT_TRIAL_NAME = "v2_eval_20_3"
    CURRENT_TRIAL_NAME = "v2_eval_20-40"
    CURRENT_TRIAL_NAME = "v2_eval_60-40"
    CURRENT_TRIAL_NAME = "v2_eval_100-35"
    CURRENT_TRIAL_NAME = "v2_eval_0-60"


    file_signature = CURRENT_TRIAL_NAME

    if CURRENT_TRIAL_NAME:
        CURRENT_TRIAL_FOLDER = TRIAL_BASE_NAME+CURRENT_TRIAL_NAME


    #Outfile related things:
    OUTFOLDER = "results"
    OUTFILE_NAME =  f"test_{file_signature}.csv"
    OUTFILE2_NAME = f"test_table_{file_signature}.txt"
    APPEND = False
    # APPEND = True



    # CURRENT_TRIAL_FOLDER = "alfworld_eval_trial_30_3"
    CSV_FILE_NAME = "alfworld_results.csv"

    file_path = os.path.join(BASE_FOLDER, CURRENT_TRIAL_FOLDER, CSV_FILE_NAME)

    with open(file_path) as csvfile:
        results = csv.reader(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        data = [row for row in results]


    current_model = ""
    current_prompt = ""
    out_results = []
    for idx,row in enumerate(data):
        if idx == 0:
            index_mapping_row, index_mapping_results = get_index_of_important_statistics(row)
            temp_results = [row[val] for _, val in index_mapping_row.items()]
            temp_headers = [key for key, _ in index_mapping_row.items()]
            # sanity check
            if temp_results == temp_headers:
                out_results.append(temp_results)
            else:
                raise Exception(f"Wrong Headers!=={temp_results}\n\n=={temp_headers}")
            continue
        
        this_rows_model = row[index_mapping_row["model"]]
        this_rows_prompt = row[index_mapping_row["keys_removed"]]

        temp_results = [row[val] for _, val in index_mapping_row.items()]
        # print(idx)
        # print(row)
        # print(temp_results)
        # print(index_mapping_results)
        temp_results = extract_correct_stats_from_string_row(temp_results, index_mapping_results)

        if not ((current_model == this_rows_model) and (current_prompt==this_rows_prompt)):
            current_model = this_rows_model
            current_prompt = this_rows_prompt
            out_results.append(temp_results)
        else:
            prev_results = out_results[-1]
            print(prev_results)
            print(temp_results)
            temp_results = accumulate_two_rows(prev_results,temp_results,index_mapping_results)
            out_results[-1] = temp_results
    

    ###########################################################
    #
    #WRITING OUT FILEs
    #
    ###########################################################
    if APPEND:
        out_file_mode = "a"
    else:
        out_file_mode = "w"

    #Writing results to a csv file
    DELIMITER = "&"
    OUTFILE = os.path.join(OUTFOLDER,OUTFILE_NAME)
    with open(OUTFILE, out_file_mode) as out_file:
        writer = csv.writer(out_file, delimiter=DELIMITER)
        for out_row in out_results:
            writer.writerow(out_row)
    print(len(out_row))
    

    #Writing a pretty printed table as text file 
    from tabulate import tabulate
    OUTFILE2 = os.path.join(OUTFOLDER,OUTFILE2_NAME)
    table_pretty = tabulate(out_results[1:], headers=IMPORTANT_STATISTICS)
    if APPEND:
        table_pretty = "\n"+"\n".join(table_pretty.split("\n")[2:])
    with open(OUTFILE2, out_file_mode) as out_file:
        out_file.write(table_pretty)

    # data = pd.read_csv(file_path)
    # data.drop()

