import numpy as np

import main
from image_analysis import select_images
import image_processor
from image_processor import ImageProcessingManager
from image_analysis.select_images import select_random_images
from image_processor import ScanningCursor
from helper_functions import load_configuration_information
from OCR import OCR_from_tiff
from PIL import Image


#Test OCR capture, make sure all the data is captured right
def test_OCR_capture():
    data_directory, data_has_been_downloaded, browser_type, download_directory = main.load_configuration_information()
    list_of_ballot_paths = select_images.select_random_images(data_directory, 50)
    for ballot_path in list_of_ballot_paths:
        print(ballot_path)
        data_page = OCR_from_tiff.capture_third_page(ballot_path)
        ballot_data = OCR_from_tiff.read_text(data_page)
        for key in ballot_data.keys():
            print(f"{key}: {ballot_data[key]}")


def test_get_border_bars():
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()
    if not data_has_been_downloaded:
        #raise RuntimeError('Configuration File says that data has not been downloaded yet')
        pass
    IM = image_processor.ImageProcessingManager()
    list_of_random_images = select_images.select_random_images(data_directory, 20)
    for random_image in list_of_random_images:
        override_image = "/home/dave/Documents/FultonCounty/Tabulator05150/Batch323/Images/05150_00323_000080.tif"
        ballot_image = Image.open(random_image)
        if override_image:
            ballot_image = Image.open(override_image)
        #list_of_random_images[0] = "/home/dave/Documents/FultonCounty/Tabulator05160/Batch181/Images/05160_00181_000071.tif"
        print("\n\neog " + random_image + "&")
        print(f"\"{random_image}\"")
        ballot_bitmap = np.asarray(ballot_image)
        ballot_image.crop( (0, 0, 1000, 1000) ).resize( (300, 300) ).show()
        Image.fromarray(ballot_bitmap[0:1000, 0:1000]).resize( (300, 300) ).show()
        cursor = image_processor.ScanningCursor()
        locations_of_top_bars, locations_of_side_bars = cursor.get_border_bars(ballot_bitmap)
        print(locations_of_top_bars)
        print(locations_of_side_bars)


def get_border_bars_better_test():
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()
    count = 0
    if not data_has_been_downloaded:
        #raise RuntimeError('Configuration File says that data has not been downloaded yet')
        pass
    IM = ImageProcessingManager()
    list_of_random_images = select_random_images(data_directory, 2000)
    for random_image in list_of_random_images:
        count += 1
        override_image = 0
        if override_image:
            random_image = override_image
        ballot_image = Image.open(random_image)
        ballot_bitmap = np.asarray(ballot_image)
        cursor = ScanningCursor()
        try:
            locations_of_top_bars, locations_of_side_bars = cursor.get_border_bars(ballot_bitmap)
        except:
            print("\n\neog " + random_image + "&")
            print(f"\"{random_image}\"")
        there_is_an_issue = (locations_of_top_bars[0][1] - locations_of_top_bars[0][0] < 15) \
                            or (locations_of_top_bars[0][1] - locations_of_top_bars[0][0] > 30) \
                            or locations_of_top_bars[0][0] > 220 \
                            or locations_of_top_bars[0][0] < 160
        if there_is_an_issue:
            print("\n\neog " + random_image + "&")
            print(f"\"{random_image}\"")
            print(locations_of_top_bars[0][1] - locations_of_top_bars[0][0], locations_of_top_bars[0:2],
                  locations_of_top_bars[-1], locations_of_top_bars[-1][1] - locations_of_top_bars[-1][0])
            print(locations_of_side_bars[0][1] - locations_of_side_bars[0][0], locations_of_side_bars[0:2],
                  locations_of_side_bars[-1], locations_of_side_bars[-1][1] - locations_of_side_bars[-1][0])


        if count % 20 == 0:
            print(f"{count} ballots so far")

    #IM.open_enlarge_compare(list_of_random_images)
    #while(True):
    #    list_of_random_images = select_random_images(data_directory, 1)
    #    IM.compare_list_of_ballots(list_of_random_images)


def circumnavigate_top_left_bar__debug_mode(image_bitmap, x_location, y_location):
    print(f"starting x location: {x_location}")
    print(f"starting y location: {y_location}")
    scanner = ScanningCursor()
    #Start by going up
    while True:
        if scanner.top_edge_has_been_reached(image_bitmap, x_location, y_location):
            break
        else:
            y_location -= 1
            print(f"x location: {x_location}")
            print(f"y location: {y_location}")
    #Start gathering data about the boundaries of the top left box
    max_x_value = x_location
    min_x_value = x_location
    max_y_value = y_location
    min_y_value = y_location
    #Move back, create a buffer zone:
    y_location += 10
    #Go right
    while True:
        if scanner.right_edge_has_been_reached(image_bitmap, x_location, y_location):
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
        if scanner.bottom_edge_has_been_reached(image_bitmap, x_location, y_location):
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
        if scanner.left_edge_has_been_reached(image_bitmap, x_location, y_location):
            break
        else:
            x_location -= 1
    #Record data:
    if x_location < min_x_value:
        min_x_value = x_location
    return min_y_value, min_x_value, max_y_value, max_x_value

