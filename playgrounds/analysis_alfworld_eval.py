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
        "keys_removed", 
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

def extract_correct_stats_from_string_row(tr, im):
    # tr[im["model"]]
    # tr[im["temperature"]]
    tr[im["success"]] = 1 if tr[im["success"]] == "True" else 0
    tr[im["done"]] = 1 if tr[im["done"]] == "True" else 0
    tr[im["total_reward"]] = float(tr[im["num_of_steps"]])
    tr[im["num_of_steps"]] = int(tr[im["num_of_steps"]])
    tr[im["num_illegal_actions"]] = int(tr[im["num_illegal_actions"]])
    tr[im["num_nothing_happens"]] = int(tr[im["num_nothing_happens"]])
    tr[im["num_repetitions"]] = int(tr[im["num_repetitions"]])
    tr[im["num_json_dsnt_load"]] = int(tr[im["num_json_dsnt_load"]])
    tr[im["num_multi_json"]] = int(tr[im["num_multi_json"]])
    tr[im["num_no_json"]] = int(tr[im["num_no_json"]])
    tr[im["num_json_and_text"]] = int(tr[im["num_json_and_text"]])
    tr[im["error"]] = 1 if tr[im["error"]] else 0
    # tr[im["keys_removed"]]
    return tr

def accumulate_two_rows(tr, pr, im):
    # tr[im["model"]]
    # tr[im["temperature"]]
    tr[im["success"]] += pr[im["success"]]
    tr[im["done"]] += pr[im["done"]]
    tr[im["total_reward"]] += pr[im["total_reward"]]
    tr[im["num_of_steps"]] += pr[im["num_of_steps"]] 
    tr[im["num_illegal_actions"]] += pr[im["num_illegal_actions"]]
    tr[im["num_nothing_happens"]] += pr[im["num_nothing_happens"]]
    tr[im["num_repetitions"]] += pr[im["num_repetitions"]]
    tr[im["num_json_dsnt_load"]] += pr[im["num_json_dsnt_load"]]
    tr[im["num_multi_json"]] += pr[im["num_multi_json"]]
    tr[im["num_no_json"]] += pr[im["num_no_json"]]
    tr[im["num_json_and_text"]] += pr[im["num_json_and_text"]]
    tr[im["error"]] += pr[im["error"]]
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
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_1"
    CURRENT_TRIAL_FOLDER = "alfworld_eval_proper_10_react_4"

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


    OUTFILE = "test2.csv"
    with open(OUTFILE, "w") as out_file:
        writer = csv.writer(out_file, delimiter='&')
        for out_row in out_results:
            writer.writerow(out_row)

    print(len(out_row))

    # data = pd.read_csv(file_path)
    # data.drop()

