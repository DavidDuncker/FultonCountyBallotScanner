import json
import os
from random import randint

import helper_functions


def select_images_from_batch(data_directory, tabulator_number, batch_number):
    selected_ballot_image_paths = []
    #Find all ballot images in data directory
    for root, directories, files in os.walk(data_directory):
        for file in files:
            conditions_are_met = (".tif" in file) \
                            and (str(tabulator_number) in file) \
                            and (str(batch_number) in file)

            if conditions_are_met:
                selected_ballot_image_paths.append(os.path.join(root, file))
    #Generate random ballots
    return selected_ballot_image_paths


def select_random_images(data_directory, number):
    all_ballot_image_paths = []
    selected_ballot_image_paths = []
    #Find all ballot images in data directory
    for root, directories, files in os.walk(data_directory):
        for file in files:
            if ".tif" in file:
                all_ballot_image_paths.append(os.path.join(root, file))
    #Generate random ballots
    for i in range(0, number):
        #Generate random number out of all possible ballots (and subtract 1 from the total number of ballots after
            #each iteration)
        lottery = randint(0, len(all_ballot_image_paths)-i)
        #Select random ballot
        selected_ballot_image_paths.append(all_ballot_image_paths[lottery])
        #Remove selected ballots from master list to prevent duplicates
        all_ballot_image_paths.pop(lottery)
    return selected_ballot_image_paths


#Input: Directory containing ballot images, JSON file containing ballot data
#Output: A list of dictionaries:
# [..., {"tabulator": ..., "batch": ..., "ballot": ..., "path": ..., "ballot data": {...} }, ...]
def select_random_ballots_with_data(data_directory, ballot_json_filepath, number_of_ballots):
    ballot_file = open(ballot_json_filepath, 'r')
    ballots = json.loads(ballot_file.read())[0]
    ballot_file.close()

    #Create a tracker to prevent the same ballot from being selected twice:
    ballot_tracker = {}
    for tabulator in ballots:
        ballot_tracker[tabulator] = {}
        for batch in ballots[tabulator]:
            ballot_tracker[tabulator][batch] = {}
            for ballot in ballots[tabulator][batch]:
                ballot_tracker[tabulator][batch][ballot] = True

    random_ballots = []
    for i in range(0, number_of_ballots):
        random_tabulator_index = randint(0, len(ballots.keys()) - 1)
        random_tabulator = list(ballots.keys())[random_tabulator_index]
        random_batch_index = randint(0, len(ballots[random_tabulator].keys()) - 1)
        random_batch = list(ballots[random_tabulator].keys())[random_batch_index]
        random_ballot_index = randint(0, len(ballots[random_tabulator][random_batch].keys()) - 1)
        random_ballot = list(ballots[random_tabulator][random_batch].keys())[random_ballot_index]
        if ballot_tracker[random_tabulator][random_batch][random_ballot] == True:
            selected_ballot = {}
            selected_ballot["tabulator"] = random_tabulator
            selected_ballot["batch"] = random_batch
            selected_ballot["ballot"] = random_ballot
            selected_ballot["filepath"] = helper_functions.get_ballot_path(data_directory, random_tabulator,
                                                                           random_batch, random_ballot)
            selected_ballot["data"] = ballots[random_tabulator][random_batch][random_ballot]
            random_ballots.append(selected_ballot)
            ballots[random_tabulator][random_batch][random_ballot] == False
        elif ballot_tracker[random_tabulator][random_batch][random_ballot] == False:
            i -= 1
            continue

    return random_ballots