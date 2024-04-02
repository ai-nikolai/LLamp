import json
import re
import os
import csv


def load_log_file(file_path):
    """ Loads game log file."""
    with open(file_path) as file:
        data = json.load(file)   
    return data

def find_first_nothing_happens(data,nothing_happens_string="Nothing happens."):
    """ Finds the first index where nothing happens."""
    for index,interaction in enumerate(data):
        if interaction["role"] == "user":
            if nothing_happens_string in interaction["content"]:
                return index

def get_action_at_index(data, index):
    """Returns the content"""
    return data[index]["content"]


def print_interactions(data,start_index):
    for x in data[start_index:]:
        print(x)    


def find_all_actions_with_nothing_happens(data, nothing_happens_string="Nothing happens."):
    """Finds and returns all actions that have nothing happens after them."""
    nothing_happens_actions = []

    for index,interaction in enumerate(data):
        if interaction["role"]=="user":
            if nothing_happens_string in interaction["content"]:
                tmp = clean_action(data[index-1]["content"])
                nothing_happens_actions.append([index-1, tmp])

    return nothing_happens_actions


def find_all_actions_valid_response(data, nothing_happens_string="Nothing happens."):
    """Finds and returns all actions that have nothing happens after them."""
    something_happens_actions = []

    for index,interaction in enumerate(data):
        if interaction["role"]=="user":
            if not (nothing_happens_string in interaction["content"]):
                tmp = clean_action(data[index-1]["content"])
                something_happens_actions.append([index-1, tmp])

    return something_happens_actions[1:]


def clean_action(action):
    """Returns a clean version of the action"""
    action = action.replace("> ","")
    action = action.replace(">","")
    action = action.replace("\n","")

    if '"action": "' in action:
        action = action.split('"action": "')[1].split('"')[0]

    return action


def check_wrong_grammar(action, verbose=False):
    """
    Checks whether the grammar was wrong
    https://regex101.com/r/89v6Kq/1
    """
    correct_grammar = False
    action = clean_action(action)
    

    put_regex = """put(?:\s\w+)(?:\s\w+)?(?:\s\d+)\sin\/on(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    goto_regex = """go\sto(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    open_regex = """open(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    take_regex = """take(?:\s\w+)(?:\s\w+)?(?:\s\d+)\sfrom(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    cool_regex = """cool(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    clean_regex = """clean(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    use_regex = """use(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    heat_regex = """heat(?:\s\w+)(?:\s\w+)?(?:\s\d+)\swith(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    examine_regex = """examine(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    close_regex = """close(?:\s\w+)(?:\s\w+)?(?:\s\d+)"""
    look_regex = """look"""

    if action.startswith("think:") or action.startswith('{"think":'):
        correct_grammar = True

    elif action.startswith("put"):
        answer = re.match(put_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action
    
    elif action.startswith("go to"):
        answer = re.match(goto_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action

    elif action.startswith("open"):
        answer = re.match(open_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action

    elif action.startswith("take"):
        answer = re.match(take_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action

    elif action.startswith("cool"):
        answer = re.match(cool_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action        

    elif action.startswith("clean"):
        answer = re.match(clean_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action    
    
    elif action.startswith("use"):
        answer = re.match(use_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action   
    
    elif action.startswith("heat"):
        answer = re.match(heat_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action  
    
    elif action.startswith("examine"):
        answer = re.match(examine_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action    

    elif action.startswith("close"):
        answer = re.match(close_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action    

    elif action.startswith("look"):
        answer = re.match(look_regex,action)
        if answer:
            correct_grammar = True
        elif verbose:
            correct_grammar="FALSE: "+action    

    else:
        if verbose:
            if len(action.split(" "))<10:
                correct_grammar = "DID NOT MATCH: "+action

    return correct_grammar





# 
def load_csv_file(file_path):
    """ Loads (results) csv file."""
    with open(file_path) as csvfile:
        results = csv.reader(csvfile, delimiter=',') #,quotechar='"', quoting=csv.QUOTE_ALL)
        data = [row for row in results]
    return data

def get_csv_header_index(header):
    """ Returns and index from header to index"""
    index = {}
    for idx, key in enumerate(header):
        index[key] = idx

    return index

def write_line_to_main_log_csv(name, data, mode="a"):
    """Writes one line of output into the main CSV"""
    with open(name, mode, newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if type(data) == list:
            wr.writerow(data)
        elif type(data) == dict:
            data_list = [x for _,x in data.items()]
            wr.writerow(data_list)


def augment_logging_dict(logging_dict, data_row, index, empty_data=False):
    """ Add a list of data to logging_dict according to index"""
    for key,idx in index.items():
        if empty_data:
            logging_dict[key] = 0
        else:
            logging_dict[key] = data_row[idx]

    return logging_dict




# 
 
def return_empty_partial_logging_dict():
    logging_dict = {
        "total_nothing" : 0,

        "total_not_valid_nothing" : 0,
        "put_not_valid_nothing" : 0,
        "hallucinated_not_valid_nothing":0,
        "fake_not_h_not_valid_nothing":0,
        "fake_command_example": "NO EXAMPLE",

        "total_valid_nothing" : 0,
        "take_valid_nothing" : 0,
        "valid_nothing_example" : "NO EXAMPLE",
    }  

    return logging_dict   

def analyse_data(data, verbose=False, return_empty=False):
    """ Creates an analysis """    
    logging_dict = return_empty_partial_logging_dict()
    
    nothing_happens_actions = find_all_actions_with_nothing_happens(data)
    logging_dict["total_nothing"] = len(nothing_happens_actions)

    for action in nothing_happens_actions:
        actual_action = action[1]
        valid_grammar = check_wrong_grammar(actual_action)

        if valid_grammar:
            logging_dict["total_valid_nothing"] += 1
            if actual_action.startswith("take"):
                logging_dict["take_valid_nothing"] += 1
            else:
                logging_dict["valid_nothing_example"] = actual_action
            if verbose:
                print(f"Valid Grammar, nothing happens:{actual_action}")

        
        else:
            logging_dict["total_not_valid_nothing"] += 1
            
            if len(actual_action.split(" "))>9:
                logging_dict["hallucinated_not_valid_nothing"] += 1
            else:
                logging_dict["fake_not_h_not_valid_nothing"] += 1
                logging_dict["fake_command_example"] = actual_action


            if actual_action.startswith("put"):
                logging_dict["put_not_valid_nothing"] += 1
  
            if verbose:
                print(f"NOT Valid Grammar, nothing happens:{actual_action}")
  
    return logging_dict


def check_all_grammar(data, verbose=False):
    """ Checks whether all grammar is correct"""
    something_happens_actions = find_all_actions_valid_response(data)

    #Go through all actions and find if some action is not in our grammar.  
    if verbose:
        for action in data:
            if action["role"]=="assistant":
                print(check_wrong_grammar(action["content"], verbose=True))

    check_all_valid_responses_have_valid_grammar = all([check_wrong_grammar(x[1]) for x in something_happens_actions])
    if verbose:
        print(f"All valid responses have valid grammar (if not add to grammar file):{check_all_valid_responses_have_valid_grammar}")
    
        if not check_all_valid_responses_have_valid_grammar:
            for action in something_happens_actions:
                if not check_wrong_grammar(action[1]):
                    print(action)

    return check_all_valid_responses_have_valid_grammar




def analysis_per_trace_file(trace_file_path, config_string=""):
    """ Analysis the whole trace file."""
    trace_data = load_log_file(trace_file_path)
    all_good = check_all_grammar(trace_data)
    if not all_good:
        print(f"Env with Config String: {config_string} has a problem with grammar.")
    logging_dict = analyse_data(trace_data)

    return logging_dict


def check_grammar_for_data_row(data_row):
    trace_file_path = data_row[data_index["trace_file"]]
    trace_data = load_log_file(trace_file_path)
    problem = check_all_grammar(trace_data, verbose=True)

if __name__=="__main__":
    """
"env_idx","env_type","agent_type","model","temperature","success","done","total_reward","num_of_steps","num_illegal_actions","num_nothing_happens","num_repetitions","num_json_dsnt_load","num_multi_json","num_no_json","num_json_and_text","error","early_stop","keys_removed","additional_prompt_annotation","trace_file","prompt_file"
"0","cool","OpenAITextChat","gpt-3.5-turbo-0125","0.0","False","True","0","49","50","12","0","50","0","50","0","","","react-1","","game_logs/alfworld_eval_v2_eval_20_3/OpenAITextChatAgent_logs_18_03_2024_15_57_25.json","game_logs/alfworld_eval_v2_eval_20_3/prompt_18_03_2024_15_57_25.txt"
    """
    MAIN_CSV_FILEPATH = "playgrounds/deepdive_results.csv"
    data = load_csv_file("playgrounds/all_results.csv")
    data_index = get_csv_header_index(data[0])

    CREATE_NEW_CSV = True
    if CREATE_NEW_CSV:
        empty_logging_dict = return_empty_partial_logging_dict()
        augment_logging_dict(empty_logging_dict,[],data_index,True)
        new_header = [key for key, val in empty_logging_dict.items()]
        write_line_to_main_log_csv(MAIN_CSV_FILEPATH, new_header, mode="w")


    for idx, experiment_data in enumerate(data[1:]):
        config_string = str(idx)+"+"+experiment_data[data_index["env_idx"]]+"+"+experiment_data[data_index["env_type"]]+"+"+experiment_data[data_index["keys_removed"]]
        trace_file_path = experiment_data[data_index["trace_file"]]
        logging_dict = analysis_per_trace_file(trace_file_path,config_string)
        augment_logging_dict(logging_dict, experiment_data, data_index)


        write_line_to_main_log_csv(MAIN_CSV_FILEPATH, logging_dict)

    # check_grammar_for_data_row(data[1425])
     


# EOF