import os
from random import randint


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