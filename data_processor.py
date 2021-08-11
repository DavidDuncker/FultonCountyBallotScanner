import os
import numpy as np
from PIL import Image

from image_processor import ScanningCursor
from image_processor import get_serial_number
from time import time
from image_processor import BallotGrid


class BubbleGridLocations:
    trump_bubble = [18, 18, 0, 0]
    biden_bubble = [21, 21, 0, 0]
    jojo_bubble = [24, 24, 0, 0]
    perdue_bubble = [32, 32, 0, 0]
    ossoff_bubble = [32, 32, 0, 0]
    hazel_bubble = [36, 36, 0, 0]
    senate_special_election = [0 for x in range(0, 20)]
    senate_special_election[0] = []
    senate_special_election[0] = [20, 20, 11, 11]
    senate_special_election[1] = []
    senate_special_election[1] = [22, 22, 11, 11]
    senate_special_election[2] = []
    senate_special_election[2] = [24, 24, 11, 11]
    senate_special_election[3] = []
    senate_special_election[3] = [26, 26, 11, 11]
    senate_special_election[4] = []
    senate_special_election[4] = [28, 28, 11, 11]
    senate_special_election[5] = []
    senate_special_election[5] = [30, 30, 11, 11]
    senate_special_election[6] = []
    senate_special_election[6] = [32, 32, 11, 11]
    senate_special_election[7] = []
    senate_special_election[7] = [34, 34, 11, 11]
    senate_special_election[8] = []
    senate_special_election[8] = [36, 36, 11, 11]
    senate_special_election[9] = []
    senate_special_election[9] = [38, 38, 11, 11]
    senate_special_election[10] = []
    senate_special_election[10] = [40, 40, 11, 11]
    senate_special_election[11] = []
    senate_special_election[11] = [42, 42, 11, 11]
    senate_special_election[12] = []
    senate_special_election[12] = [44, 44, 11, 11]
    senate_special_election[13] = []
    senate_special_election[13] = [46, 46, 11, 11]
    senate_special_election[14] = []
    senate_special_election[14] = [48, 48, 11, 11]
    senate_special_election[15] = []
    senate_special_election[15] = [50, 50, 11, 11]
    senate_special_election[16] = []
    senate_special_election[16] = [52, 52, 11, 11]
    senate_special_election[17] = []
    senate_special_election[17] = [54, 54, 11, 11]
    senate_special_election[18] = []
    senate_special_election[18] = [56, 56, 11, 11]
    senate_special_election[19] = []
    senate_special_election[19] = [58, 58, 11, 11]

    downballot_candidates = range(0, 21)
    downballot_candidates[0] = []
    downballot_candidates[0] = [18, 18, 22, 22]
    downballot_candidates[1] = []
    downballot_candidates[1] = []
    downballot_candidates[2] = []
    downballot_candidates[2] = []
    downballot_candidates[3] = []
    downballot_candidates[3] = []
    downballot_candidates[4] = []
    downballot_candidates[4] = []
    downballot_candidates[5] = []
    downballot_candidates[5] = []
    downballot_candidates[6] = []
    downballot_candidates[6] = []
    downballot_candidates[7] = []
    downballot_candidates[7] = []
    downballot_candidates[8] = []
    downballot_candidates[8] = []
    downballot_candidates[9] = []
    downballot_candidates[9] = []
    downballot_candidates[10] = []
    downballot_candidates[10] = []
    downballot_candidates[11] = []
    downballot_candidates[11] = []
    downballot_candidates[12] = []
    downballot_candidates[12] = []
    downballot_candidates[13] = []
    downballot_candidates[13] = []
    downballot_candidates[14] = []
    downballot_candidates[14] = []
    downballot_candidates[15] = []
    downballot_candidates[15] = []
    downballot_candidates[16] = []
    downballot_candidates[16] = []
    downballot_candidates[17] = []
    downballot_candidates[17] = []
    downballot_candidates[18] = []
    downballot_candidates[18] = []
    downballot_candidates[19] = []
    downballot_candidates[19] = []
    downballot_candidates[20] = []
    downballot_candidates[20] = []


#Input: the directory containing all the ballot images
#Output: A dictionary. barcode_directory[<int tabulator>][<int batch>][<int ballot number>] = int barcode
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


#Input: A dictionary. barcode_directory[<int tabulator>][<int batch>][<int ballot number>] = int barcode
#Output: A list. Catalogue[<int number>] =
#                   [list of batches with a barcode that appears that many times consecutively]
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


#I'm pretty sure this is scrap
def scan_ballot_grid(image_data):
    #Load Scanning Cursor
    cursor = ScanningCursor()
    #Get the location of all the black rectangles on the border
    locations_of_top_bars, locations_of_side_bars, locations_of_bottom_bars, \
    left_bar_data, right_bar_data = cursor.get_border_bars(image_data)
    #Create function that takes in 2 numbers and outputs the area of the ballot associated with those grid numbers:


if __name__ == "__main__":
    data_directory = "/home/dave/Documents/FultonCounty"
    path = "/home/dave/Documents/FultonCounty/Tabulator05162/Batch063/Images/05162_00063_000057.tif"
    ballot_grid = BallotGrid(path)
    grid_area = ballot_grid.get_grid_image_with_padding(18, 18, 22, 22, 5, 5, 0, 15)
    Image.fromarray(grid_area).resize( (1200, 400) ).show()


