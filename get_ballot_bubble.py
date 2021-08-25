import os
import time

from PIL import Image, ImageSequence

import helper_functions
import select_images
from grids_and_bubbles import BallotGrid
from helper_functions import load_configuration_information
import numpy as np

TOP = 0
BOTTOM = 1
LEFT = 2
RIGHT = 3

class BallotGridCrops:
    path_to_image = ""
    first_page_image_data = False
    second_page_image_data = False
    grid = False
    grid_page_two = False
    bubble = {}
    bubble["Trump"] = [18, 18, 0, 0]
    bubble["Biden"] = [21, 21, 0, 0]
    bubble["Jorgensen"] = [24, 24, 0, 0]
    bubble["P_WriteIn"] = [27, 27, 0, 0]
    pres_OCR_to_crop_dictionary = {'Writ': 'P_WriteIn', 'Jose': 'Biden', 'Dona': 'Trump', 'JoJo': 'Jorgensen'}

    bubble["Perdue"] = [32, 32, 0, 0]
    bubble["Ossoff"] = [34, 34, 0, 0]
    bubble["Hazel"] = [36, 36, 0, 0]
    bubble["S_WriteIn"] = [38, 38, 0, 0]
    senate_OCR_to_crop_dictionary = {'Davi': "Perdue", 'JonO': "Ossoff", 'Shan': "Hazel", 'Writ': "S_WriteIn"}

    bubble["Bartell"] = [20, 20, 11, 11]
    bubble["Buckley"] = [22, 22, 11, 11]
    bubble["Collins"] = [24, 24, 11, 11]
    bubble["Fortuin"] = [26, 26, 11, 11]
    bubble["Grayson"] = [28, 28, 11, 11]
    bubble["Greene"] = [30, 30, 11, 11]
    bubble["AJackson"] = [32, 32, 11, 11]
    bubble["DJackson"] = [34, 34, 11, 11]
    bubble["James"] = [36, 36, 11, 11]
    bubble["Johnson"] = [38, 38, 11, 11]
    bubble["Shealey"] = [40, 40, 11, 11]
    bubble["Lieberman"] = [42, 42, 11, 11]
    bubble["Loeffler"] = [44, 44, 11, 11]
    bubble["Slade"] = [46, 46, 11, 11]
    bubble["Slowinski"] = [48, 48, 11, 11]
    bubble["Stovall"] = [50, 50, 11, 11]
    bubble["Tarver"] = [52, 52, 11, 11]
    bubble["Taylor"] = [54, 54, 11, 11]
    bubble["Warnock"] = [56, 56, 11, 11]
    bubble["Winfield"] = [58, 58, 11, 11]
    bubble["SS_WriteIn"] = [60, 60, 11, 11]
    special_senate_OCR_to_crop_dictionary = \
        {'Kell': "Loeffler", 'Raph': "Warnock", 'Doug': "Collins", 'Debo': "DJackson", 'Mich': "Greene",
         'EdTa': "Tarver", 'John': "Fortuin", 'AlBa': "Bartell", 'Matt': "Lieberman", 'Rich': "Winfield",
         'Tama': "Shealey", 'JoyF': "Slade", 'Alle': "Buckley", 'Kand': "Taylor", 'Jame': "James",
         'Bria': "Slowinski", 'Vale': "Stovall", 'Derr': "Grayson", 'Anne': "AJackson", 'Writ': "SS_WriteIn",
         'AWay': "Johnson"}

    rightside_bubble = [[] for x in range(0, 14)]
    rightside_bubble[0] = [18, 18, 22, 22]
    rightside_bubble[1] = [20, 20, 22, 22]
    rightside_bubble[2] = [22, 22, 22, 22]
    rightside_bubble[3] = [24, 24, 22, 22]

    rightside_bubble[4] = [29, 29, 22, 22]
    rightside_bubble[5] = [31, 31, 22, 22]
    rightside_bubble[6] = [33, 33, 22, 22]
    rightside_bubble[7] = [35, 35, 22, 22]

    rightside_bubble[8] = [40, 40, 22, 22]
    rightside_bubble[9] = [42, 42, 22, 22]
    rightside_bubble[10] = [44, 44, 22, 22]

    rightside_bubble[11] = [49, 49, 22, 22]
    rightside_bubble[12] = [51, 51, 22, 22]
    rightside_bubble[13] = [53, 53, 22, 22]

    second_page_bubbles = [[] for x in range(118)]
    second_page_bubbles[0] = [2, 2, 0, 0]
    second_page_bubbles[1] = [3, 3, 0, 0]
    second_page_bubbles[2] = [4, 4, 0, 0]
    second_page_bubbles[3] = [5, 5, 0, 0]
    second_page_bubbles[4] = [6, 6, 0, 0]
    second_page_bubbles[5] = [7, 7, 0, 0]
    second_page_bubbles[6] = [8, 8, 0, 0]
    second_page_bubbles[7] = [9, 9, 0, 0]
    second_page_bubbles[8] = [10, 10, 0, 0]
    second_page_bubbles[9] = [11, 11, 0, 0]
    second_page_bubbles[10] = [12, 12, 0, 0]
    second_page_bubbles[11] = [13, 13, 0, 0]
    second_page_bubbles[12] = [14, 14, 0, 0]
    second_page_bubbles[13] = [15, 15, 0, 0]
    second_page_bubbles[14] = [16, 16, 0, 0]
    second_page_bubbles[15] = [17, 17, 0, 0]
    second_page_bubbles[16] = [18, 18, 0, 0]
    second_page_bubbles[17] = [19, 19, 0, 0]
    second_page_bubbles[18] = [20, 20, 0, 0]
    second_page_bubbles[19] = [21, 21, 0, 0]
    second_page_bubbles[20] = [22, 22, 0, 0]
    second_page_bubbles[21] = [23, 23, 0, 0]
    second_page_bubbles[22] = [24, 24, 0, 0]
    second_page_bubbles[23] = [25, 25, 0, 0]
    second_page_bubbles[24] = [26, 26, 0, 0]
    second_page_bubbles[25] = [27, 27, 0, 0]
    second_page_bubbles[26] = [28, 28, 0, 0]
    second_page_bubbles[27] = [29, 29, 0, 0]
    second_page_bubbles[28] = [30, 30, 0, 0]
    second_page_bubbles[29] = [31, 31, 0, 0]
    second_page_bubbles[30] = [32, 32, 0, 0]
    second_page_bubbles[31] = [33, 33, 0, 0]
    second_page_bubbles[32] = [34, 34, 0, 0]
    second_page_bubbles[33] = [35, 35, 0, 0]
    second_page_bubbles[34] = [36, 36, 0, 0]
    second_page_bubbles[35] = [37, 37, 0, 0]
    second_page_bubbles[36] = [38, 38, 0, 0]
    second_page_bubbles[37] = [39, 39, 0, 0]
    second_page_bubbles[38] = [40, 40, 0, 0]
    second_page_bubbles[39] = [41, 41, 0, 0]
    second_page_bubbles[40] = [42, 42, 0, 0]
    second_page_bubbles[41] = [43, 43, 0, 0]
    second_page_bubbles[42] = [44, 44, 0, 0]
    second_page_bubbles[43] = [45, 45, 0, 0]
    second_page_bubbles[44] = [46, 46, 0, 0]
    second_page_bubbles[45] = [47, 47, 0, 0]
    second_page_bubbles[46] = [48, 48, 0, 0]
    second_page_bubbles[47] = [49, 49, 0, 0]
    second_page_bubbles[48] = [50, 50, 0, 0]
    second_page_bubbles[49] = [51, 51, 0, 0]
    second_page_bubbles[50] = [52, 52, 0, 0]
    second_page_bubbles[51] = [53, 53, 0, 0]
    second_page_bubbles[52] = [54, 54, 0, 0]
    second_page_bubbles[53] = [55, 55, 0, 0]
    second_page_bubbles[54] = [56, 56, 0, 0]
    second_page_bubbles[55] = [57, 57, 0, 0]
    second_page_bubbles[56] = [58, 58, 0, 0]
    second_page_bubbles[57] = [59, 59, 0, 0]
    second_page_bubbles[58] = [60, 60, 0, 0]
    second_page_bubbles[59] = [2, 2, 11, 11]
    second_page_bubbles[60] = [3, 3, 11, 11]
    second_page_bubbles[61] = [4, 4, 11, 11]
    second_page_bubbles[62] = [5, 5, 11, 11]
    second_page_bubbles[63] = [6, 6, 11, 11]
    second_page_bubbles[64] = [7, 7, 11, 11]
    second_page_bubbles[65] = [8, 8, 11, 11]
    second_page_bubbles[66] = [9, 9, 11, 11]
    second_page_bubbles[67] = [10, 10, 11, 11]
    second_page_bubbles[68] = [11, 11, 11, 11]
    second_page_bubbles[69] = [12, 12, 11, 11]
    second_page_bubbles[70] = [13, 13, 11, 11]
    second_page_bubbles[71] = [14, 14, 11, 11]
    second_page_bubbles[72] = [15, 15, 11, 11]
    second_page_bubbles[73] = [16, 16, 11, 11]
    second_page_bubbles[74] = [17, 17, 11, 11]
    second_page_bubbles[75] = [18, 18, 11, 11]
    second_page_bubbles[76] = [19, 19, 11, 11]
    second_page_bubbles[77] = [20, 20, 11, 11]
    second_page_bubbles[78] = [21, 21, 11, 11]
    second_page_bubbles[79] = [22, 22, 11, 11]
    second_page_bubbles[80] = [23, 23, 11, 11]
    second_page_bubbles[81] = [24, 24, 11, 11]
    second_page_bubbles[82] = [25, 25, 11, 11]
    second_page_bubbles[83] = [26, 26, 11, 11]
    second_page_bubbles[84] = [27, 27, 11, 11]
    second_page_bubbles[85] = [28, 28, 11, 11]
    second_page_bubbles[86] = [29, 29, 11, 11]
    second_page_bubbles[87] = [30, 30, 11, 11]
    second_page_bubbles[88] = [31, 31, 11, 11]
    second_page_bubbles[89] = [32, 32, 11, 11]
    second_page_bubbles[90] = [33, 33, 11, 11]
    second_page_bubbles[91] = [34, 34, 11, 11]
    second_page_bubbles[92] = [35, 35, 11, 11]
    second_page_bubbles[93] = [36, 36, 11, 11]
    second_page_bubbles[94] = [37, 37, 11, 11]
    second_page_bubbles[95] = [38, 38, 11, 11]
    second_page_bubbles[96] = [39, 39, 11, 11]
    second_page_bubbles[97] = [40, 40, 11, 11]
    second_page_bubbles[98] = [41, 41, 11, 11]
    second_page_bubbles[99] = [42, 42, 11, 11]
    second_page_bubbles[100] = [43, 43, 11, 11]
    second_page_bubbles[101] = [44, 44, 11, 11]
    second_page_bubbles[102] = [45, 45, 11, 11]
    second_page_bubbles[103] = [46, 46, 11, 11]
    second_page_bubbles[104] = [47, 47, 11, 11]
    second_page_bubbles[105] = [48, 48, 11, 11]
    second_page_bubbles[106] = [49, 49, 11, 11]
    second_page_bubbles[107] = [50, 50, 11, 11]
    second_page_bubbles[108] = [51, 51, 11, 11]
    second_page_bubbles[109] = [52, 52, 11, 11]
    second_page_bubbles[110] = [53, 53, 11, 11]
    second_page_bubbles[111] = [54, 54, 11, 11]
    second_page_bubbles[112] = [55, 55, 11, 11]
    second_page_bubbles[113] = [56, 56, 11, 11]
    second_page_bubbles[114] = [57, 57, 11, 11]
    second_page_bubbles[115] = [58, 58, 11, 11]
    second_page_bubbles[116] = [59, 59, 11, 11]
    second_page_bubbles[117] = [60, 60, 11, 11]

    def __init__(self, path_to_image):
        self.path_to_image = path_to_image
        image = Image.open(path_to_image)
        self.first_page_image_data = np.asarray(image)
        image.close()
        self.grid = BallotGrid(self.first_page_image_data)

    def get_second_page(self):
        second_page_image_data = False
        page_count = 0
        image = Image.open(self.path_to_image)
        for page in ImageSequence.Iterator(image):
            page_count += 1
            if page_count == 2:
                self.second_page_image_data = np.asarray(page)
                self.grid_page_two = BallotGrid(self.second_page_image_data)
                return self.second_page_image_data

    def bubble_is_filled_in(self, image_data):
        #Count the zeros in array
        cropped_image_data = self.crop_to_content(image_data)
        found_letters_not_bubbles = (cropped_image_data.shape[0] < 15) \
                                or (cropped_image_data.shape[0] > 40) \
                                or (cropped_image_data.shape[1] < 20) \
                                or (cropped_image_data.shape[1] > 40)
        if found_letters_not_bubbles:
            return False
        number_of_black_pixels = np.count_nonzero(cropped_image_data == 0)
        number_of_white_pixels = np.sum(cropped_image_data)
        proportion_of_black_pixels = float(number_of_black_pixels/(number_of_black_pixels+number_of_white_pixels))
        if proportion_of_black_pixels <= 0.5:
            return False
        else:
            return True

    #Input: Numpy array representing image date
    #Output: Numpy array representing that same image data, except with the all-white
        #rows and all-white columns removed
    def crop_to_content(self, image_data):
        #Find non-empty rows and columns
        #"0" means black (i.e. content we want), and "1" means white (i.e. whitespace)
        non_empty_columns = np.where(image_data.min(axis=0) < 1)[0]
        non_empty_rows = np.where(image_data.min(axis=1) < 1)[0]
        #Create a 4-tuple for the dimensions of the cropped imaged
        try:
            cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
        except ValueError:
            #If it's already been cropped, then the arguments for "min" will be an empty sequence
            return image_data
        #Crop the image data
        cropped_image_data = image_data[cropBox[0]:cropBox[1] + 1, cropBox[2]:cropBox[3] + 1]
        return cropped_image_data

    def check_all_rightside_bubbles(self):
        filled_in_bubbles = []
        for bubble in self.rightside_bubble:
            image = self.grid.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM], bubble[LEFT], bubble[RIGHT],
                                                     5, 5, 5, 25)
            #Image.fromarray(image).resize( (400, 300) ).show()
            bubble_is_filled_in = self.bubble_is_filled_in(image)
            if bubble_is_filled_in:
                filled_in_bubbles.append(bubble)
        return filled_in_bubbles

    def check_all_second_page_bubbles(self):
        filled_in_bubbles = []
        for bubble in self.second_page_bubbles:
            image = self.grid_page_two.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM], bubble[LEFT],
                                                                   bubble[RIGHT], 25, 25, 10, 20)
            #Image.fromarray(image).resize( (400, 300) ).show()
            bubble_is_filled_in = self.bubble_is_filled_in(image)
            if bubble_is_filled_in:
                filled_in_bubbles.append(bubble)
                #Image.fromarray(image).resize((400, 300)).show()
                image = self.crop_to_content(image)
                #print(f"cropped image.shape[0]: {image.shape[0]}")
                #print(f"cropped image.shape[1]: {image.shape[1]}\n\n")
                pass
        return filled_in_bubbles

    #Input: 2 Numpy arrays that represent images
    #Output: A percentage (number between 0 and 1) representing how similar they are
    def compare_two_bubbles(self, image1_data, image2_data):
        number_of_rows = image1_data.shape[0]
        number_of_columns = image1_data.shape[1]
        number_of_similarities = 0
        number_of_comparisons = 0
        for row in range(0, number_of_rows):
            for column in range(0, number_of_columns):
                try:
                    match = not (image1_data[row][column] ^ image2_data[row][column])
                    number_of_similarities += match
                    number_of_comparisons += 1
                except:
                    pass
        return number_of_similarities/number_of_comparisons


def get_ballot_bubble_locations(ballot_info):
    ballot_bubble_locations = []
    set_of_crops = BallotGridCrops(ballot_info['filepath'])

    ballot_president_vote = ballot_info['data']['President']
    bubble_locator = set_of_crops.pres_OCR_to_crop_dictionary[ballot_president_vote]
    president_bubble = set_of_crops.bubble[bubble_locator]
    ballot_bubble_locations.append(president_bubble)

    ballot_senate_vote = ballot_info['data']['Senate']
    bubble_locator = set_of_crops.senate_OCR_to_crop_dictionary[ballot_senate_vote]
    senate_bubble = set_of_crops.bubble[bubble_locator]
    ballot_bubble_locations.append(senate_bubble)

    ballot_special_senate_vote = ballot_info['data']['Special Senate']
    bubble_locator = set_of_crops.special_senate_OCR_to_crop_dictionary[ballot_special_senate_vote]
    special_senate_bubble = set_of_crops.bubble[bubble_locator]
    ballot_bubble_locations.append(special_senate_bubble)

    right_side_bubbles = set_of_crops.check_all_rightside_bubbles()
    ballot_bubble_locations.extend(right_side_bubbles)

    return ballot_bubble_locations


if __name__ == "__main__":
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()
    ballot_path = '/home/dave/Documents/FultonCounty/Tabulator05160/Batch181/Images/05160_00181_000029.tif'
    #ballot_path = select_images.select_random_images(data_directory, 1)[0]
    ballot_json_path = "/data/FultonCounty/ballot_directory.json"
    grid_manager = BallotGridCrops(ballot_path)
    grid_manager.get_second_page()
    ballot_info = helper_functions.transform_ballot_path_into_ballot_info_object(ballot_path, ballot_json_path)
    first_page_bubbles = get_ballot_bubble_locations(ballot_info)
    second_page_bubbles = grid_manager.check_all_second_page_bubbles()
    #[top, bottom, left, right] = [5, 5, 11, 11]
    for bubble in first_page_bubbles:
        bubble_image = grid_manager.grid.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM], bubble[LEFT],
                                                                      bubble[RIGHT], 10, 10, 10, 20)
        expanded_bubble_image = grid_manager.grid.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM],
                                                                               bubble[LEFT], bubble[RIGHT],
                                                                               20, 20, 10, 40)
        #Image.fromarray(bubble_image).show()
        #Image.fromarray(expanded_bubble_image).show()

    for bubble in second_page_bubbles:
        bubble_image = grid_manager.grid_page_two.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM], bubble[LEFT],
                                                                      bubble[RIGHT], 10, 10, 10, 20)
        expanded_bubble_image = grid_manager.grid_page_two.get_grid_image_with_padding(bubble[TOP], bubble[BOTTOM],
                                                                               bubble[LEFT], bubble[RIGHT],
                                                                               20, 20, 10, 300)
        #Image.fromarray(bubble_image).show()
        Image.fromarray(expanded_bubble_image).show()



