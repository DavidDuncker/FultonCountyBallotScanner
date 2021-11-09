import csv
import os
import json
from helper_functions import update_nested_dict


def read_all_files(gwinnett_directory_path):
    ballot_directory = {}
    for root, directories, files in os.walk(gwinnett_directory_path):
        for file in files:
            csv_path = os.path.join(root, file)
            with open(csv_path) as csv_file:
                reader = csv.DictReader(csv_file,
                                        fieldnames=['filename', 'tabulator', 'batch', 'ballot', 'time', 'scanner',
                                                    'Poll ID', "Ballot ID", "President", "Senate", "Special Senate",
                                                    "hash"])
                for row in reader:
                    tabulator = row['tabulator']
                    batch = row['batch']
                    ballot_number = row['ballot']
                    ballot_directory = update_nested_dict(ballot_directory, tabulator, batch, ballot_number, value=row)
    return ballot_directory


if __name__ == "__main__":
    directory = "/home/dave/Documents/Election Fraud/Ballot images/GwinnettCounty"
    read_all_files(directory)
