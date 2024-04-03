import csv
import json
import os 
import yaml


def augment_logging_dict(logging_dict, data_row, index, empty_data=False):
    """ Add a list of data to logging_dict according to index"""
    for key,idx in index.items():
        if empty_data:
            logging_dict[key] = 0
        else:
            logging_dict[key] = data_row[idx]

    return logging_dict

def write_line_to_main_log_csv(name, data, mode="a"):
    """Writes one line of output into the main CSV"""
    with open(name, mode, newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if type(data) == list:
            wr.writerow(data)
        elif type(data) == dict:
            data_list = [x for _,x in data.items()]
            wr.writerow(data_list)


def get_csv_header_index(header):
    """ Returns and index from header to index"""
    index = {}
    for idx, key in enumerate(header):
        index[key] = idx

    return index



def load_csv_file(file_path):
    """ Loads (results) csv file."""
    with open(file_path) as csvfile:
        results = csv.reader(csvfile, delimiter=',') #,quotechar='"', quoting=csv.QUOTE_ALL)
        data = [row for row in results]
    return data


def load_log_file(file_path):
    """ Loads game log file."""
    with open(file_path) as file:
        data = json.load(file)   
    return data