import json
import os
import sys


def find_matches_ballots_in_duplicate_batches():
    import json
    identical_batches = [['/794/25', '/791/32 (difference = 5) '], ['/794/20', '/791/28 (difference = 8) '],
                         ['/794/21', '/791/29 (difference = 13) '], ['/791/19', '/791/26 (difference = 0) '],
                         ['/791/17', '/791/24 (difference = 0) '], ['/791/24', '/791/17 (difference = 0) '],
                         ['/791/26', '/791/19 (difference = 0) '], ['/791/25', '/791/18 (difference = 0) '],
                         ['/791/20', '/791/23 (difference = 8) '], ['/791/29', '/794/21 (difference = 13) '],
                         ['/791/28', '/794/20 (difference = 8) '], ['/791/32', '/794/25 (difference = 5) '],
                         ['/791/23', '/791/20 (difference = 8) '], ['/791/18', '/791/25 (difference = 0) '],
                         ['/816/7', '/816/3 (difference = 22) '], ['/816/5', '/816/6 (difference = 22) '],
                         ['/816/3', '/816/7 (difference = 22) '], ['/816/6', '/816/5 (difference = 22) '],
                         ['/773/24', '/773/22 (difference = 0) '], ['/773/22', '/773/24 (difference = 0) '],
                         ['/802/80', '/802/78 (difference = 0) '], ['/802/78', '/802/80 (difference = 0) '],
                         ['/742/42', '/742/40 (difference = 6) '], ['/742/40', '/742/42 (difference = 6) ']]

    ballot_path = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/ballot_directory_recount.json"
    ballot_file = open(ballot_path, 'r')
    ballot_data = json.loads(ballot_file.read())[0]
    ballot_file.close()
    for pair in identical_batches:
        tabulator1 = pair[0].split('/')[1]
        batch1 = pair[0].split('/')[2]

        tabulator2 = pair[1].split(' ')[0].split("/")[1]
        batch2 = pair[1].split(' ')[0].split("/")[2]

        ballots1 = ballot_data[tabulator1][batch1].keys()
        ballots2 = ballot_data[tabulator1][batch1].keys()
        for ballot_number1 in ballots1:
            matches = []
            for ballot_number2 in ballots2:
                hash1 = ballot_data[tabulator1][batch1][ballot_number1]["hash"]
                hash2 = ballot_data[tabulator2][batch2][ballot_number2]["hash"]
                if hash1 == hash2:
                    matches.append(ballot_number2)
            print(f"Tabulator {tabulator1}, Batch {batch1}, Ballot Number {ballot_number1} matches up with:")
            if len(matches) == 0:
                print("\t\tNothing")
            else:
                for match in matches:
                    print(f"\t\tTabulator {tabulator2}, Batch {batch2}, Ballot Number {match}")


def load_configuration_information():
    try:
        #Open configuration file
        configuration_file = open(".config", 'r')
    except FileNotFoundError:
        #Create configuration file with input from user
        configuration_file = open(".config", 'w')

        new_configuration_file_contents = ""
        new_configuration_file_contents += "Directory for downloaded data (no quotations, please): " + os.linesep
        new_configuration_file_contents += input("Enter the directory for the downloaded data (no quotes): "
                                                 + os.linesep) + os.linesep
        new_configuration_file_contents += "Have the files been downloaded completely? " + os.linesep
        new_configuration_file_contents += "False" + os.linesep
        new_configuration_file_contents += "Selenium Webdriver: Chrome or Firefox?: " + os.linesep
        new_configuration_file_contents += input("You need to install Selenium Webdriver to download the data; Will you "
                                                 "use Firefox or Chrome?"  + os.linesep).capitalize() + os.linesep
        new_configuration_file_contents += "Download folder to search for downloaded data: " + os.linesep
        new_configuration_file_contents += input("Now what is your selenium browser's default "
                                                 "download folder? " + os.linesep) + os.linesep

        configuration_file.write(new_configuration_file_contents)
        configuration_file.close()
        configuration_file = open(".config", 'r')

    all_lines_in_file = configuration_file.readlines()
    data_directory = all_lines_in_file[1].strip()
    data_has_been_downloaded = all_lines_in_file[3].strip() != "False" #Only way to convert string to bool
    browser_type = all_lines_in_file[5].strip()
    download_directory = all_lines_in_file[7].strip()
    return data_directory, data_has_been_downloaded, browser_type, download_directory


def get_ballot_path(data_directory, tabulator, batch, ballot):
    if len(str(int(tabulator))) == 1:
        tabulator_path_string = "Tabulator0000" + str(int(tabulator))
        tabulator_file_string = "0000" + str(int(tabulator))
    elif len(str(int(tabulator))) == 2:
        tabulator_path_string = "Tabulator000" + str(int(tabulator))
        tabulator_file_string = "000" + str(int(tabulator))
    elif len(str(int(tabulator))) == 3:
        tabulator_path_string = "Tabulator00" + str(int(tabulator))
        tabulator_file_string = "00" + str(int(tabulator))
    elif len(str(int(tabulator))) == 4:
        tabulator_path_string = "Tabulator0" + str(int(tabulator))
        tabulator_file_string = "0" + str(int(tabulator))
    elif len(str(int(tabulator))) == 5:
        tabulator_path_string = "Tabulator" + str(int(tabulator))
        tabulator_file_string = "" + str(int(tabulator))

    if len(str(int(batch))) == 1:
        batch_path_string = "Batch00" + str(int(batch))
        batch_file_string = "0000" + str(int(batch))
    elif len(str(int(batch))) == 2:
        batch_path_string = "Batch0" + str(int(batch))
        batch_file_string = "000" + str(int(batch))
    elif len(str(int(batch))) == 3:
        batch_path_string = "Batch" + str(int(batch))
        batch_file_string = "00" + str(int(batch))

    if len(str(int(ballot))) == 1:
        ballot_file_string = "00000" + str(int(ballot))
    elif len(str(int(ballot))) == 2:
        ballot_file_string = "0000" + str(int(ballot))
    elif len(str(int(ballot))) == 3:
        ballot_file_string = "000" + str(int(ballot))
    elif len(str(int(ballot))) == 4:
        ballot_file_string = "00" + str(int(ballot))

    filename = f"{tabulator_file_string}_{batch_file_string}_{ballot_file_string}.tif"
    path = os.path.join(data_directory, tabulator_path_string, batch_path_string, "Images", filename)
    return path


def transform_ballot_path_into_ballot_info_object(ballot_path, ballot_json_collection_path):
    ballot_file = ballot_path.split("/")[-1][0:-4]
    tabulator = str(int(ballot_file.split("_")[0]))
    batch = str(int(ballot_file.split("_")[1]))
    ballot_number = str(int(ballot_file.split("_")[2]))
    ballot_collection_file = open(ballot_json_collection_path, 'r')
    ballot_collection = json.loads(ballot_collection_file.read())[0]
    ballot_collection_file.close()
    try:
        ballot = {}
        ballot["tabulator"] = tabulator
        ballot["batch"] = batch
        ballot["ballot"] = ballot_number
        ballot["filepath"] = ballot_path
        ballot["data"] = ballot_collection[tabulator][batch][ballot_number]
    except:
        ballot = False
        print(sys.exc_info()[2])
    return ballot



