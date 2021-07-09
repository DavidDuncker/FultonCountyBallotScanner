import os
import numpy as np
from PIL import Image
from image_processor import ScanningCursor
from image_processor import get_serial_number
import main
import json
from time import time


#Walk through all the files, scan their barcodes, and save the data into a python dictionary
#That python dictionary can be saved into a json file.
def scan_all_barcodes(data_directory):
    #Count the number of files, so we can keep track of progress
    total_number_of_files = 0
    for root, directories, files in os.walk(data_directory):
        for file in files:
            total_number_of_files += 1
    print(f"Total number of files: {total_number_of_files}")
    number_of_processed_files = 0

    #Initialize final dictionary of barcodes
    barcode_directory = {}
    #Set up directory crawl
    timer_start = time()
    for root, directories, files in os.walk(data_directory):
        for file in files:
            barcode = 0
            tabulator = int(root.split("/")[5][-5:])
            batch = int(root.split("/")[6][-3:])
            full_file_name = os.path.join(root, file)
            #Get the barcode, or label it as a software error
            try:
                # Create image
                img = Image.open(full_file_name)
                    #We have to put that line under "try" just in case Image tries to open "Thumbs.db"
                # Turn image into numpy array
                image_data = np.asarray(img)
                img.close()
                barcode = get_serial_number(image_data)
            except:
                barcode = "software error"
            try:
                ballot_number = int(file[-6:-4])
                barcode_directory[tabulator][batch][ballot_number] = barcode
            except ValueError: #Sometimes the file isn't a ballot file; it might crash the program
                continue
            except KeyError:
                try:
                    barcode_directory[tabulator][batch] = {}
                    barcode_directory[tabulator][batch][ballot_number] = barcode
                except KeyError:
                    barcode_directory[tabulator] = {}
                    barcode_directory[tabulator][batch] = {}
                    barcode_directory[tabulator][batch][ballot_number] = barcode
            number_of_processed_files += 1

            #Display updates:
            if number_of_processed_files == 10 or number_of_processed_files == 50 \
                    or number_of_processed_files == 100 or number_of_processed_files % 500 == 0:
                    print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                    timer = time()
                    print(f"Time elapsed (in seconds): {timer - timer_start}")
    return barcode_directory


#For each batch, we need to catalogue:
    #1. The number of unique ballots in the batch
    #2. The number of 2 consecutive bar codes, and the starting point
    #3. The number of 3 consecutive bar codes, and the starting point
    #4. The number of 4 or more consecutive bar codes, and the starting point.
    #5. The highest number of consecutive barcodes, and the starting point
def catalogue_consecutive_barcodes(barcode_dictionary):
    catalogue_of_consecutive_groups_of_ballots = [0 for x in range(0, 150)]
    #Populate the dictionary with zeros
    for number in range(0, 150):
        catalogue_of_consecutive_groups_of_ballots[number] = []
    for tabulator in barcode_dictionary.keys():
        for batch in barcode_dictionary[tabulator].keys():
            #Create variable to decrement when it is shown that a ballot is not a unique ballot
            list_of_ballots = [ballot for ballot in barcode_dictionary[tabulator][batch].keys()]
            list_of_ballots.sort()
            ballot_is_part_of_consecutive_group = False
            number_of_consecutive_ballots = 0
            first_in_consecutive_group = None
            for ballot in range(0, len(list_of_ballots)):
                ballot_number = list_of_ballots[ballot]
                barcode = barcode_dictionary[tabulator][batch][ballot_number]
                #Exclude errors
                if barcode == "software error":
                    continue
                try:
                    next_ballot_number = list_of_ballots[ballot + 1]
                    next_barcode = barcode_dictionary[tabulator][batch][next_ballot_number]
                    if next_barcode == barcode:
                        number_of_consecutive_ballots += 1
                        if not ballot_is_part_of_consecutive_group:
                            first_in_consecutive_group = list_of_ballots[ballot]
                        ballot_is_part_of_consecutive_group = True


                    else:
                        if ballot_is_part_of_consecutive_group:
                            catalogue_of_consecutive_groups_of_ballots[number_of_consecutive_ballots]\
                                .append(f"/{tabulator}/{batch}/{first_in_consecutive_group}")
                        number_of_consecutive_ballots = 0
                        ballot_is_part_of_consecutive_group = False
                        first_in_consecutive_group = None
                except IndexError:
                    pass
    return catalogue_of_consecutive_groups_of_ballots







if __name__ == "__main__":
    barcode_file = open("barcodes.json", 'r')
    barcode_dictionary = json.loads( barcode_file.read() )
    consecutive_barcodes = catalogue_consecutive_barcodes(barcode_dictionary)
    for number in range(2, len(consecutive_barcodes)):
        print(f"{number}: \n {consecutive_barcodes[number]}")
        print("")



