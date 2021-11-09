import csv
from helper_functions import post_updates

FULTON_PATH = "/home/dave/Documents/Election Fraud/canvass/Election_Ballot_Applications.csv"
STATEWIDE_PATH = "/home/dave/Documents/Election Fraud/canvass/STATEWIDE.csv"

def read_eba_files(fulton_path=FULTON_PATH, statewide_path=STATEWIDE_PATH):
    fulton_eba_file = open(fulton_path, 'r')
    fulton_eba_reader = csv.DictReader(fulton_eba_file)
    fulton_eba_keys = next(fulton_eba_reader).keys()

    statewide_eba_file = open(statewide_path, 'r')
    statewide_eba_reader = csv.DictReader(statewide_eba_file)
    statewide_eba_keys = next(statewide_eba_reader).keys()

    common_columns = []
    for statewide_column in statewide_eba_keys:
        for fulton_column in fulton_eba_keys:
            if statewide_column.lower().replace(" #", "") in fulton_column.lower():
                if fulton_column.lower() not in common_columns:
                    common_columns.append(fulton_column.lower())

    print(f"Common Columns:\n\t{common_columns}")
    #print(f"Fulton Columns:\n\t{fulton_eba_keys}")
    #print(f"Statewide Columns:\n\t{statewide_eba_keys}")

    print("Getting list of Fulton data")
    fulton_eba_file = open(fulton_path, 'r', errors='replace')
    fulton_eba_reader = csv.DictReader(fulton_eba_file)
    dict_of_fulton_data = {}
    for row in fulton_eba_reader:
        output_string = ""
        for column1 in common_columns:
            for column2 in fulton_eba_keys:
                if column1 == column2.lower().replace(" #", ""):
                    value = row[column2].strip()
                    value = value.replace("false", "NO")
                    value = value.replace("-", "")
                    try:
                        output_string += str(int(value)) + ","
                    except ValueError:
                        output_string += value + ","
        output_string = output_string[:-1]
        dict_of_fulton_data.update({output_string: None})

    print("Getting list of statewide data for Fulton County")
    statewide_eba_file = open(statewide_path, 'r', errors='replace')
    statewide_eba_reader = csv.DictReader(statewide_eba_file)
    dict_of_statewide_data = {}
    for row in statewide_eba_reader:
        output_string = ""
        if row["County"] != "FULTON":
            continue
        for column1 in common_columns:
            for column2 in statewide_eba_keys:
                if column1 == column2.lower().replace(" #", ""):
                    value = row[column2].strip()
                    value = value.replace("false", "NO")
                    value = value.replace("-", "")
                    try:
                        output_string += str(int(value)) + ","
                    except ValueError:
                        output_string += value + ","
        output_string = output_string[:-1]
        dict_of_statewide_data.update({output_string: None})

    return common_columns, dict_of_fulton_data, dict_of_statewide_data


def find_differences_in_EBA_files():
    columns, dict_of_fulton_data, dict_of_statewide_data = read_eba_files()
    count = 0

    print("Finding fulton data not in statewide data")
    fulton_data_not_in_statewide_data = []
    for fulton_data in dict_of_fulton_data.keys():
        count+=1
        post_updates(count, [1,10,100,1000,10000,100000,1000000])
        if fulton_data not in dict_of_statewide_data.keys():
            fulton_data_not_in_statewide_data.append(fulton_data)

    print("Finding statewide data not in fulton data")
    count=0
    statewide_data_not_in_fulton_data = []
    for statewide_data in dict_of_statewide_data.keys():
        count+=1
        post_updates(count, [1,10,100,1000,10000,100000,1000000])
        if statewide_data not in dict_of_fulton_data.keys():
            statewide_data_not_in_fulton_data.append(statewide_data)

    print("About to return values")
    return columns, fulton_data_not_in_statewide_data, statewide_data_not_in_fulton_data, \
           dict_of_fulton_data, dict_of_statewide_data

