#The idea here is to get a list of addresses for fraternities and sororities, and then use those addresses to find
#people who live at a fraternity or sorority who is over the age of 24 that voted in the election.

#If a frat or sorority member over 24 years old voted in an election, then chances are that they
#graduated and someone else voted in their name

import csv
import os
import json


def get_frat_addresses(frat_address_filepath):
    frat_address_file = open(frat_address_filepath, 'r')
    frat_address_text = frat_address_file.read()
    frat_address_file.close()

    frat_addresses = []
    for fraternity in frat_address_text.split("\n\n"):
        frat_addresses.append(fraternity.split("\n")[1])

    return frat_addresses


def get_EBA_addresses(eba_csv, eba_json_savefile_path):
    ebas = []

    if os.path.isfile(eba_json_savefile_path):
        eba_json_savefile = open(eba_json_savefile_path, 'r')
        ebas = json.loads(eba_json_savefile.read())
        eba_json_savefile.close()
    else:
        with open(eba_csv, 'r') as eba_file:
            eba_reader = csv.reader(eba_file, delimiter=",")
            columns = next(eba_reader)
            for row in eba_reader:
                row_data = {}
                for column in range(0, len(row)):
                    row_data[columns[column]] = row[column]
                ebas.append(row_data)
        eba_json_savefile = open(eba_json_savefile_path, 'w')
        eba_json_savefile.write(json.dumps(ebas))
        eba_json_savefile.close()

    return ebas



def match_addresses(frat_address_filepath, eba_csv, eba_json_savefile_path):
    frat_addresses = get_frat_addresses(frat_address_filepath)
    ebas = get_EBA_addresses(eba_csv, eba_json_savefile_path)

    frat_voters = []

    for eba in ebas:
        eba_strnum = eba["Street"]
        eba_strname = eba["Street Name"].upper()
        eba_city = eba["City"].upper()
        eba_state = eba["State"].upper()
        eba_zip = eba["Zip Code"]
        for frat in frat_addresses:
            frat_strnum = frat.split(",")[0].split(" ")[0]
            frat_strname = ' '.join(frat.split(",")[0].split(" ")[1:]).upper()
            frat_city = frat.split(",")[1].replace(" ", "").upper()
            frat_state = frat.split(",")[2].split(" ")[1]
            frat_zip = frat.split(",")[2].split(" ")[2]
            if (frat_strnum == eba_strnum) and (frat_strname == eba_strname) and (frat_city == eba_city) and \
                (frat_state == eba_state) and (frat_zip == eba_zip):
                frat_voters.append(eba)
    return frat_voters




if __name__ == "__main__":
    frat_address_filepath = "/home/dave/Documents/Election Fraud/GreekAngle/AtlantaFrats.txt"
    eba_csv = "/home/dave/Documents/Election Fraud/GreekAngle/Election_Ballot_Applications.csv"
    eba_json_savefile_path = "/data/FultonCounty/eba.json"
    age_filepath = "/home/dave/Documents/Election Fraud/GreekAngle/" \
                   "Active_Voters_by_Race_and_Gender_by_Age_Group_by_County_with_Statewide_Totals2.xlsx"
    voter_history_filepaths = ["/home/dave/Documents/Election Fraud/Voter_removal/2019.TXT",
                               "/home/dave/Documents/Election Fraud/Voter_removal/2020.TXT",
                               "/home/dave/Documents/Election Fraud/Voter_removal/2021.TXT"]
    match_addresses(frat_address_filepath, eba_csv, eba_json_savefile_path)