import csv
from collections import defaultdict
from helper_functions import post_updates, recursively_de_infinitize_dictionary
import os


def recursively_increment_tally(tally_dictionary, list_of_attributes):
    attribute = list_of_attributes.pop(0)
    if "Write-in" in attribute:
        attribute = "Write-in"
    if len(list_of_attributes) == 0:
        try:
            tally_dictionary[attribute] += 1
        except TypeError:
            tally_dictionary[attribute] = 1
        return tally_dictionary

    else:
        tally_dictionary[attribute] = recursively_increment_tally(tally_dictionary[attribute], list_of_attributes)
        return tally_dictionary
    return tally_dictionary


def get_list_of_attributes(row, variables_to_tally):
    list_of_attributes = []
    for variable in variables_to_tally:
        for key in row.keys():
            if variable.lower().replace(" ", "") in key.lower().replace(" ", ""):
                list_of_attributes.append(row[key])

    return list_of_attributes


#
##Example usage:
##tally = get_tally('Fulton Ballots.csv', 'precinct/tabulator/President')
##tally['I1L']['5150']['Donald J Trump'] = 1523
#
def get_tally(ballot_csv, tally_string):
    infinitely_deep_dictionary = lambda: defaultdict(infinitely_deep_dictionary)
    final_tally = infinitely_deep_dictionary()

    variables_to_tally = tally_string.split("/")
    with open(ballot_csv) as ballots:
        reader = csv.DictReader(ballots)
        row_count = 0
        for row in reader:
            row_count += 1
            post_updates(row_count, [1, 10, 100, 1000, 10000])

            list_of_attributes = get_list_of_attributes(row, variables_to_tally)
            final_tally = recursively_increment_tally(final_tally, list_of_attributes)

    final_tally = recursively_de_infinitize_dictionary(final_tally)

    return final_tally


def trim_tally_to_top_candidates(tally, number_of_top_candidates):
    trimmed_tally = {}
    for key in tally.keys():
        trimmed_tally[key] = {key: value for key, value in sorted(tally[key].items(), key=lambda item: item[1], reverse=True)[0:number_of_top_candidates]}
    return trimmed_tally


def print_results_for_2D_tally(tally):
    output_string = ""
    list_of_columns = []
    for row in tally.keys():
        for column in tally[row].keys():
            if column not in list_of_columns:
                list_of_columns.append(column)

    output_string += "Precinct,"
    for column in list_of_columns:
        output_string += f"{column},"

    output_string += "\n"

    for row in tally.keys():
        output_string += f"{row},"
        for column in list_of_columns:
            try:
                output_string += f"{tally[row][column]},"
            except KeyError:
                output_string += "0,"
        output_string += "\n"

    return output_string


def run_tally_for_entire_directory(ocr_directory, save_directory, tally_string="precinct/President"):
    dictionary_of_tallies = {}
    for root, dirs, files in os.walk(ocr_directory):
        for file in files:
            if ".csv" in file:
                path_to_ocr = os.path.join(root, file)
                print(f"{path_to_ocr}:")
                tally = get_tally(path_to_ocr, tally_string)
                #trimmed_tally = trim_tally_to_top_candidates(tally, 4)
                csv_output = print_results_for_2D_tally(tally)
                dictionary_of_tallies.update({file: csv_output})

                savefile_name = file[0:-4] + "_tally.csv"
                savefile_path = os.path.join(save_directory, savefile_name)
                savefile = open(savefile_path, 'w')
                savefile.write(csv_output)
                savefile.close()

    return dictionary_of_tallies
