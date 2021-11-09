import csv
import json
import os
from duplicates import dupe_sequences


def create_ballot_dict(path):
    with open(path) as csv_file:
        ballot_directory = {}
        reader = csv.DictReader(csv_file)
        for row in reader:
            standard_format = {}
            for key in row.keys():
                if key == None:
                    continue
                if "file" in key.lower() and "name" in key.lower():
                    filename = row[key]
                    standard_format["filename"] = filename
                elif "tabulator" in key.lower():
                    tabulator = row[key]
                elif "batch" in key.lower():
                    batch = row[key]
                elif "ballot" in key.lower():
                    ballot = row[key]
                elif "adjud" in key.lower():
                    adjudicated = row[key]
                    standard_format["adjudicated"] = adjudicated
                elif "presid" in key.lower():
                    president = row[key]
                    standard_format["President"] = president
                elif "hash" in key.lower() or "signat" in key.lower():
                    hash = row[key]
                    standard_format["hash"] = hash
            try:
                ballot_directory[tabulator][batch][ballot] = row
                ballot_directory[tabulator][batch][ballot].update(standard_format)
            except KeyError:
                try:
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot] = row
                    ballot_directory[tabulator][batch][ballot].update(standard_format)

                except KeyError:
                    ballot_directory[tabulator] = {}
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot] = row
                    ballot_directory[tabulator][batch][ballot].update(standard_format)

    return ballot_directory


def find_duplicates(path):
    ballot_directory = create_ballot_dict(path)
    adjacent_hash_directory = dupe_sequences.create_hash_directory(ballot_directory, 5)
    matches = dupe_sequences.find_sequences_of_dupes(adjacent_hash_directory, True, 1)
    return matches

def find_duplicates_in_folder(path):
    dictonary_of_matches = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".csv" in file:
                path_to_ocr = os.path.join(root, file)
                print(f"{path_to_ocr}:")
                try:
                    matches = find_duplicates(path_to_ocr)
                    print(matches)
                    dictonary_of_matches.update({file: matches})
                except:
                    print("Encountered an error. Moving on. \n\n")

    return dictonary_of_matches
