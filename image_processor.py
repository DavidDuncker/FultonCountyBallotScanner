import numpy as np
from PIL import Image
from helper_functions import load_configuration_information
import os
from random import randint
from time import sleep
from time import time

#Black pixels are labeled as "0" or "False"
#White pixels are labeled as "1" or "True"
#Black pixels contain the information we want
BLACK = 0
WHITE = 1


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


class BallotGrid:
    top_grid_bars = []
    left_grid_bars = []
    bottom_grid_bars = []
    left_bar_code_rectangle = []
    right_bar_code_rectangle = []
    image_data = np.array(0)

    def __init__(self, path_to_ballot_image):
        #Open Image
        ballot_image = Image.open(path_to_ballot_image)
        #Turn image into numpy array
        self.image_data = np.asarray(ballot_image)
        #Close Image
        ballot_image.close()
        #Get the locations of the grid bars
        cursor = ScanningCursor()
        self.top_grid_bars, self.left_grid_bars, self.bottom_grid_bars, \
            self.left_bar_code_rectangle, self.right_bar_code_rectangle = cursor.get_border_bars(self.image_data)

    def get_grid_image(self, top_grid_row, bottom_grid_row, left_grid_column, right_grid_column):
        top = self.left_grid_bars[top_grid_row][0]
        bottom = self.left_grid_bars[bottom_grid_row][1]
        left = self.top_grid_bars[left_grid_column][0]
        right = self.bottom_grid_bars[right_grid_column][1]
        grid_based_cropped_image = self.image_data[top:bottom, left:right]
        return grid_based_cropped_image

    def get_grid_image_with_padding(self, top_grid_row, bottom_grid_row, left_grid_column, right_grid_column, top_padding, bottom_padding, left_padding, right_padding):
        top = self.left_grid_bars[top_grid_row][0]
        bottom = self.left_grid_bars[bottom_grid_row][1]
        left = self.top_grid_bars[left_grid_column][0]
        right = self.bottom_grid_bars[right_grid_column][1]
        grid_based_cropped_image = self.image_data[top-top_padding:bottom+bottom_padding, left-left_padding:right+right_padding]
        return grid_based_cropped_image


#We can use the vertical and horizontal bars on the margins of the ballot to help us locate where ballot markers
    #and bubbles are expected to be on the ballot image. To this end, we can create a "Scanning Cursor" to
    #locate the x positions of the vertical edges of the top and bottom bars,
    #and the y positions of the horizontal edges of the left and right bars,
    #and use linear interpolations to focus on a specific area on the ballot where information might be.
    #Essentially, this scanning cursor is an object that will help us establish a grid on the ballot.h
class ScanningCursor:
    x_location = 0
    y_location = 0
    #Number of pixels in the "front-facing pole" to test to see if cursor is entering a side:
    front_pole_size = 2
    #Number of pixels in the "rear-facing pole" to test to see if cursor is leaving a side:
    rear_pole_size = 1

    def get_border_bars(self, image_bitmap):
        #Start by finding any point on the top left bar
        starting_x, starting_y = self.search_for_top_left_bar(image_bitmap)
        #Next, find the borders of the top left bar
        top_left_top_edge, top_left_left_edge, top_left_bottom_edge, top_left_right_edge = \
            self.circumnavigate_top_left_bar(image_bitmap, starting_x, starting_y)
        #Next, find the best point that will allow you to scan for the other bars
        starting_x = int(top_left_left_edge * 0.9 + top_left_right_edge*0.1)
        starting_y = int(top_left_top_edge*0.5 + top_left_bottom_edge*0.5)
        #Scan for the x positions of the edges of the horizontal bars
        locations_of_side_bars = self.scan_horizontal_bars(image_bitmap, starting_x, starting_y)
        locations_of_top_bars = self.scan_vertical_bars(image_bitmap, starting_x, starting_y)
        #We need to get the locations of the sides of the bottom left big bar:
        starting_y = int( locations_of_side_bars[-1][0] * 0.5 + locations_of_side_bars[-1][1] * 0.5 )
        bottom_left_top_edge, bottom_left_left_edge, bottom_left_bottom_edge, bottom_left_right_edge = \
            self.circumnavigate_top_left_bar(image_bitmap, starting_x, starting_y)
        #Now we need to get the bottom-side grid bars
        locations_of_bottom_bars = self.scan_vertical_bars(image_bitmap, starting_x, starting_y)
        #Now we need to locate the leftside column of the ballot bar code
        starting_x = int( bottom_left_left_edge * 0.1 + bottom_left_right_edge * 0.9 )
        #If we start in the middle of the bottom left bar, then go up by the length of the bottom left bar,
        # that should place the cursor inside of the left-most bar code column
        starting_y = (bottom_left_top_edge + bottom_left_bottom_edge)/2 \
                      - (bottom_left_bottom_edge - bottom_left_top_edge)
        starting_y = int(starting_y)
        #Now we need to scan the boundaries of the left-most bar
        left_bar_top_edge, left_bar_left_edge, left_bar_bottom_edge, left_bar_right_edge = \
            self.circumnavigate_top_left_bar(image_bitmap, starting_x, starting_y)
        #Now we need to find a point inside the right-most bar
        starting_x = locations_of_bottom_bars[9][0] * 0.5 + locations_of_bottom_bars[9][1] * 0.5
        starting_x = int(starting_x)
        starting_y = (left_bar_top_edge + left_bar_bottom_edge)/2
        starting_y = int(starting_y)
        right_bar_top_edge, right_bar_left_edge, right_bar_bottom_edge, right_bar_right_edge = \
            self.circumnavigate_top_left_bar(image_bitmap, starting_x, starting_y)

        left_bar_data = [left_bar_left_edge, left_bar_top_edge, left_bar_right_edge, left_bar_bottom_edge]
        right_bar_data = [right_bar_left_edge, right_bar_top_edge, right_bar_right_edge, right_bar_bottom_edge]

        return locations_of_top_bars, locations_of_side_bars, locations_of_bottom_bars, left_bar_data, right_bar_data

    #The top-left bar sets the standards for the location of all the other bars
    #This function will simply find a single point on the surface of that bar
    def search_for_top_left_bar(self, image_bitmap):
        x_location = 0
        y_location = 0
        current_pixel_color = image_bitmap[y_location][x_location]
        #Avoid any left-side borders
        while current_pixel_color == BLACK:
            x_location += 1
            current_pixel_color = image_bitmap[y_location][x_location]

        while current_pixel_color == WHITE:
            #Keep moving down 2 pixels for every 1 pixel to the right until we hit a black pixel
            x_location += 1
            y_location += 2
            current_pixel_color = image_bitmap[y_location][x_location]
            #Go deeper, just to make sure you didn't hit a glitchy black line
            if current_pixel_color == BLACK:
                x_location += 20
                y_location += 20
                current_pixel_color = image_bitmap[y_location][x_location]
        return x_location, y_location

    def circumnavigate_top_left_bar(self, image_bitmap, x_location, y_location):
        #Start by going up
        while True:
            if self.top_edge_has_been_reached(image_bitmap, x_location, y_location):
                break
            else:
                y_location -= 1
        #Start gathering data about the boundaries of the top left box
        max_x_value = x_location
        min_x_value = x_location
        max_y_value = y_location
        min_y_value = y_location
        #Move back, create a buffer zone:
        y_location += 10
        #Go right
        while True:
            if self.right_edge_has_been_reached(image_bitmap, x_location, y_location):
                break
            else:
                x_location += 1
        #Record data:
        if x_location > max_x_value:
            max_x_value = x_location
        #Move back, create a buffer zone:
        x_location -= 10

        #Go down:
        while True:
            if self.bottom_edge_has_been_reached(image_bitmap, x_location, y_location):
                break
            else:
                y_location += 1
        #Record data:
        if y_location > max_y_value:
            max_y_value = y_location
        #Move back, create a buffer zone:
        y_location -= 10
        #Go left
        while True:
            if self.left_edge_has_been_reached(image_bitmap, x_location, y_location):
                break
            else:
                x_location -= 1
        #Record data:
        if x_location < min_x_value:
            min_x_value = x_location
        return min_y_value, min_x_value, max_y_value, max_x_value

    def scan_vertical_bars(self, image_bitmap, starting_x, starting_y):
        x_location = starting_x
        y_location = starting_y
        list_of_vertical_bars = []
        left_edge = False
        while True:
            try:
                x_location += 1
                if self.left_edge_has_been_reached(image_bitmap, x_location, y_location):
                    left_edge = x_location
                if self.right_edge_has_been_reached(image_bitmap, x_location, y_location) and left_edge:
                    right_edge = x_location
                    list_of_vertical_bars.append([left_edge, right_edge])
                    left_edge = False
            except IndexError:
                return list_of_vertical_bars

    def scan_horizontal_bars(self, image_bitmap, starting_x, starting_y):
        x_location = starting_x
        y_location = starting_y
        list_of_horizontal_bars = []
        top_edge = False
        while True:
            try:
                y_location += 1
                if self.top_edge_has_been_reached(image_bitmap, x_location, y_location):
                    top_edge = y_location
                if self.bottom_edge_has_been_reached(image_bitmap, x_location, y_location) and top_edge:
                    bottom_edge = y_location
                    list_of_horizontal_bars.append([top_edge, bottom_edge])
                    top_edge = False
            except IndexError:
                return list_of_horizontal_bars

    def top_edge_has_been_reached(self, image_bitmap, x_location, y_location):
        sum_of_white_pixels_in_front_pole = 0
        sum_of_white_pixels_in_back_pole = 0
        for y in range(y_location-1, y_location-self.front_pole_size-1, -1):
            sum_of_white_pixels_in_front_pole += image_bitmap[y][x_location]
        for y in range(y_location+1, y_location+self.rear_pole_size+1, 1):
            sum_of_white_pixels_in_back_pole += image_bitmap[y][x_location]
        if sum_of_white_pixels_in_front_pole == self.front_pole_size-1\
                and sum_of_white_pixels_in_back_pole == 0:
            return True
        else:
            return False

    def right_edge_has_been_reached(self, image_bitmap, x_location, y_location):
        sum_of_white_pixels_in_front_pole = 0
        sum_of_white_pixels_in_back_pole = 0
        for x in range(x_location+1, x_location+self.front_pole_size+1, 1):
            sum_of_white_pixels_in_front_pole += image_bitmap[y_location][x]
        for x in range(x_location-1, x_location-self.rear_pole_size-1, -1):
            sum_of_white_pixels_in_back_pole += image_bitmap[y_location][x]
        if sum_of_white_pixels_in_front_pole == self.front_pole_size-1\
                and sum_of_white_pixels_in_back_pole == 0:
            return True
        else:
            return False

    def bottom_edge_has_been_reached(self, image_bitmap, x_location, y_location):
        sum_of_white_pixels_in_front_pole = 0
        sum_of_white_pixels_in_back_pole = 0
        for y in range(y_location+1, y_location+self.front_pole_size+1, 1):
            sum_of_white_pixels_in_front_pole += image_bitmap[y][x_location]
        for y in range(y_location-1, y_location-self.rear_pole_size-1, -1):
            sum_of_white_pixels_in_back_pole += image_bitmap[y][x_location]
        if sum_of_white_pixels_in_front_pole == self.front_pole_size-1\
                and sum_of_white_pixels_in_back_pole == 0:
            return True
        else:
            return False

    def left_edge_has_been_reached(self, image_bitmap, x_location, y_location):
        sum_of_white_pixels_in_front_pole = 0
        sum_of_white_pixels_in_back_pole = 0
        for x in range(x_location-1, x_location-self.front_pole_size-1, -1):
            sum_of_white_pixels_in_front_pole += image_bitmap[y_location][x]
        for x in range(x_location+1, x_location+self.rear_pole_size+1, 1):
            sum_of_white_pixels_in_back_pole += image_bitmap[y_location][x]
        if sum_of_white_pixels_in_front_pole == self.front_pole_size-1\
                and sum_of_white_pixels_in_back_pole  == 0:
            return True
        else:
            return False

def locate_grid_bars(image_bitmap):
    scanning_cursor = ScanningCursor()
    top_grid_bars, left_grid_bars = scanning_cursor.get_border_bars(image_bitmap)


class ImageProcessingManager:
    leftside_bubble_crop = (180, 1120, 230, 2165)
    trump_bubble_crop = (175, 1105, 230, 1185)
    biden_bubble_crop = (175, 1255, 230, 1335)
    perdue_bubble_crop = (175, 1805, 230, 1880)
    ossoff_bubble_crop = (175, 1905, 230, 1980)


    def compare_list_of_ballots(self, list_of_image_paths):
        list_of_available_crops = [self.trump_bubble_crop, self.biden_bubble_crop,
                                   self.perdue_bubble_crop, self.ossoff_bubble_crop]

        for first_image_index in range(0, len(list_of_image_paths)):
            #Get the image path
            image_path = list_of_image_paths[first_image_index]
            #Open the image
            image_object = Image.open(image_path)
            #Check which bubbles are filled in, and only allow cropping towards filled-in bubbles
            valid_crops = []
            cropped_first_images = {}
            for cropping_scheme in list_of_available_crops:
                cropped_image = image_object.crop(cropping_scheme)
                image_data = np.asarray(cropped_image)
                bubble_is_filled, cropped_first_image = self.bubble_is_filled_in(image_data)
                if bubble_is_filled:
                    valid_crops.append(cropping_scheme)
                    cropped_first_images[cropping_scheme] = cropped_first_image

            for second_image_index in range(first_image_index+1, len(list_of_image_paths)):
                timer_start = time()
                #Get the image path
                second_image_path = list_of_image_paths[second_image_index]
                #Crop to the bubbles, then enlarge
                second_image_object = Image.open(second_image_path)
                # Create 2-dimensional array
                second_image_data = np.asarray(second_image_object)
                #Set up for taking the average value of comparisons
                bubble_comparison_results = []
                bubble_comparison_average = 0

                #Test each filled-in bubble
                for cropping_scheme in range(0, len(valid_crops)):
                    #Crop to bubble, crop out the whitespace, then turn into numpy array
                    cropped_first = cropped_first_images[ valid_crops[cropping_scheme] ]

                    cropped_second = second_image_object.crop(valid_crops[cropping_scheme])
                    cropped_second = np.asarray(cropped_second)
                    cropped_second = self.crop_to_content(cropped_second)

                    #Now do the comparison
                    comparison_result = self.compare_two_bubbles(cropped_first, cropped_second)
                    bubble_comparison_results.append(comparison_result)
                try:
                    bubble_comparison_average = sum(bubble_comparison_results)/len(bubble_comparison_results)
                except ZeroDivisionError:
                    bubble_comparison_average = 0
                second_image_object.close()
                if bubble_comparison_average > 0.995:
                    print(f"Average similarity between bubbles: {bubble_comparison_average}")
                    print(f"eog {image_path} &")
                    print(f"eog {second_image_path} &")
                    print("")

                #Print out results from timer... occasionally
                timer = time()
                dice = randint(0, 10000)
                if dice == -1:
                    print(f"Timer: {timer - timer_start}")
                    print(f"eog {image_path} &")
                    print(f"eog {second_image_path} &")
                    print("")
                    print(f"Average similarity between bubbles: {bubble_comparison_average}")
                    print("")
                    print("")
            image_object.close()

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

    def open_enlarge_compare(self, list_of_image_paths):
        for image_path in list_of_image_paths:
            #Open
            image_object = Image.open(image_path)
            #Crop to the bubbles, then enlarge
            image_object = image_object.crop(self.biden_bubble_crop).resize((50, 50))
            #Crop to content, then show
            #image_object = self.crop_to_content(image_object)
            image_object.show()
            image_data = np.asarray(image_object)
            self.bubble_is_filled_in(image_data)


    def bubble_is_filled_in(self, image_data):
        #Count the zeros in array
        cropped_image_data = self.crop_to_content(image_data)
        number_of_black_pixels = np.count_nonzero(cropped_image_data == 0)
        number_of_white_pixels = np.sum(cropped_image_data)
        proportion_of_black_pixels = number_of_black_pixels/(number_of_black_pixels+number_of_white_pixels)
        if proportion_of_black_pixels <= 0.25:
            return False, cropped_image_data
        else:
            return True, cropped_image_data


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


def get_serial_number(image_bitmap):
    cursor = ScanningCursor()
    locations_of_top_bars, locations_of_side_bars, locations_of_bottom_bars, \
    left_bar_data, right_bar_data = cursor.get_border_bars(image_bitmap)
    #left_bar_data and locations_of_bottom_bars are the key to getting the locations of the bits in the bar code
    location_of_barcode_bits = [0 for x in range(0, 18)] #(row, column)
    for i in range(0, 18):
        location_of_barcode_bits[i] = [0 for x in range(0, 2)]
    location_of_barcode_bits[0][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[2][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[4][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[6][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[8][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[10][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[12][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[14][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4
    location_of_barcode_bits[16][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])/4

    location_of_barcode_bits[1][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[3][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[5][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[7][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[9][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[11][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[13][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[15][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4
    location_of_barcode_bits[17][0] = left_bar_data[1] + (left_bar_data[3]-left_bar_data[1])*3/4

    location_of_barcode_bits[0][1] = locations_of_bottom_bars[0][0] + \
                                     (locations_of_bottom_bars[0][1] - locations_of_bottom_bars[0][0])/2
    location_of_barcode_bits[1][1] = locations_of_bottom_bars[0][0] + \
                                     (locations_of_bottom_bars[0][1] - locations_of_bottom_bars[0][0])/2
    location_of_barcode_bits[2][1] = locations_of_bottom_bars[1][0] + \
                                     (locations_of_bottom_bars[1][1] - locations_of_bottom_bars[1][0])/2
    location_of_barcode_bits[3][1] = locations_of_bottom_bars[1][0] + \
                                     (locations_of_bottom_bars[1][1] - locations_of_bottom_bars[1][0])/2
    location_of_barcode_bits[4][1] = locations_of_bottom_bars[2][0] + \
                                     (locations_of_bottom_bars[2][1] - locations_of_bottom_bars[2][0])/2
    location_of_barcode_bits[5][1] = locations_of_bottom_bars[2][0] + \
                                     (locations_of_bottom_bars[2][1] - locations_of_bottom_bars[2][0])/2
    location_of_barcode_bits[6][1] = locations_of_bottom_bars[3][0] + \
                                     (locations_of_bottom_bars[3][1] - locations_of_bottom_bars[3][0])/2
    location_of_barcode_bits[7][1] = locations_of_bottom_bars[3][0] + \
                                     (locations_of_bottom_bars[3][1] - locations_of_bottom_bars[3][0])/2
    location_of_barcode_bits[8][1] = locations_of_bottom_bars[4][0] + \
                                     (locations_of_bottom_bars[4][1] - locations_of_bottom_bars[4][0])/2
    location_of_barcode_bits[9][1] = locations_of_bottom_bars[4][0] + \
                                     (locations_of_bottom_bars[4][1] - locations_of_bottom_bars[4][0])/2
    location_of_barcode_bits[10][1] = locations_of_bottom_bars[5][0] + \
                                     (locations_of_bottom_bars[5][1] - locations_of_bottom_bars[5][0])/2
    location_of_barcode_bits[11][1] = locations_of_bottom_bars[5][0] + \
                                     (locations_of_bottom_bars[5][1] - locations_of_bottom_bars[5][0])/2
    location_of_barcode_bits[12][1] = locations_of_bottom_bars[6][0] + \
                                     (locations_of_bottom_bars[6][1] - locations_of_bottom_bars[6][0])/2
    location_of_barcode_bits[13][1] = locations_of_bottom_bars[6][0] + \
                                     (locations_of_bottom_bars[6][1] - locations_of_bottom_bars[6][0])/2
    location_of_barcode_bits[14][1] = locations_of_bottom_bars[7][0] + \
                                     (locations_of_bottom_bars[7][1] - locations_of_bottom_bars[7][0])/2
    location_of_barcode_bits[15][1] = locations_of_bottom_bars[7][0] + \
                                     (locations_of_bottom_bars[7][1] - locations_of_bottom_bars[7][0])/2
    location_of_barcode_bits[16][1] = locations_of_bottom_bars[8][0] + \
                                     (locations_of_bottom_bars[8][1] - locations_of_bottom_bars[8][0])/2
    location_of_barcode_bits[17][1] = locations_of_bottom_bars[8][0] + \
                                     (locations_of_bottom_bars[8][1] - locations_of_bottom_bars[8][0])/2

    #Make everything into an integer:
    for i in range(0,18):
        for j in range(0,2):
            location_of_barcode_bits[i][j] = int(location_of_barcode_bits[i][j])

    barcode = 0
    for bar in range(0, 18):
        row = location_of_barcode_bits[bar][0]
        col = location_of_barcode_bits[bar][1]
        if image_bitmap[row:row+1, col:col+1][0][0] == 0:
            #Then we're looking at a black dot. Time to add a "1"to the binary representation of the bar code
            barcode += 2**bar
    return barcode


if __name__ == "__main__":
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()
    number_of_comparisons_made = 0
    while True:
        list_of_random_images = select_random_images(data_directory, 100)
        IM = ImageProcessingManager()
        IM.compare_list_of_ballots(list_of_random_images)
        number_of_comparisons_made += 4950
        if number_of_comparisons_made % (4950*30) == 0:
            print(f"Number of comparisons made: {number_of_comparisons_made}")


