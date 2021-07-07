import numpy as np
from PIL import Image
from helper_functions import load_configuration_information
import os
from random import randint
from time import sleep
from time import time
import image_processor
from image_processor import ImageProcessingManager
from image_processor import select_random_images
from image_processor import ScanningCursor
from helper_functions import load_configuration_information


def test_get_border_bars():
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()
    if not data_has_been_downloaded:
        #raise RuntimeError('Configuration File says that data has not been downloaded yet')
        pass
    IM = image_processor.ImageProcessingManager()
    list_of_random_images = image_processor.select_random_images(data_directory, 20)
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