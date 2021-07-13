import json

from PIL import Image, ImageSequence
import pytesseract
import numpy as np

import main
import select_images
import os
from time import time


def capture_third_page(path_to_image):
    image = Image.open(path_to_image)
    page_count = 0
    data_page = None
    for page in ImageSequence.Iterator(image):
        page_count += 1
        if page_count == 3:
            data_page = page
    return data_page


def read_text(image_with_data):
    #Read text with image
    output_with_whitespace = pytesseract.image_to_string(image_with_data)
    #Remove all spaces from image for more reliability
    output = output_with_whitespace.replace(" ", "").replace(".", "")
    #Get rid of any accidental double, triple, or quadruple linebreaks
    output = output.replace("\n\n", "\n")
    output = output.replace("\n\n", "\n")
    output = output.replace("\n\n", "\n")

    #Split into lines
    lines = output.split("\n")
    #Create dictionary with all the important attributes of the ballot
    ballot_data = {}

    bookmark1 = lines[0].find("scannedat:")
    bookmark2 = lines[0].find("on")
    ballot_data["filename"] = lines[0][0:bookmark1]
    ballot_data["time"] = lines[0][bookmark1+10:bookmark2]
    ballot_data["date"] = lines[0][bookmark2+2:]

    bookmark1 = lines[1].find("Scannedon:")
    bookmark2 = lines[1].find("Tabulator:")
    bookmark3 = lines[1].find("Batch:")
    ballot_data["scanned_on"] = lines[1][bookmark1+10:bookmark2]
    ballot_data["Tabulator"] = lines[1][bookmark2+10:bookmark3]
    ballot_data["Batch"] = lines[1][bookmark3+6:]

    bookmark1 = lines[2].find("PollID:")
    bookmark2 = lines[2].find("BallotID:")
    ballot_data["Poll ID"] = lines[2][bookmark1+7:bookmark2]
    ballot_data["Ballot ID"] = lines[2][bookmark2+9:]

    ballot_data["President"] = lines[4][:4]
    ballot_data["Senate"] = lines[6][:4]
    ballot_data["Special Senate"] = lines[8][:4]
    ballot_data["PSC1"] = lines[10][:4]
    ballot_data["PSC2"] = lines[12][:4]
    ballot_data["Race6"] = lines[14][:6]
    ballot_data["Race7"] = lines[16][:6]
    ballot_data["Race8"] = lines[18][:6]
    ballot_data["Race9"] = lines[20][:6]
    ballot_data["Race10"] = lines[22][:6]
    ballot_data["Race11"] = lines[24][:6]
    ballot_data["Race12"] = lines[26][:6]
    ballot_data["Race13"] = lines[28][:6]
    ballot_data["Race14"] = lines[30][:6]

    #Create a single hash to represent the complete, maximally unique data on the entire ballot
    #First, strip all whitespace for maximum reliability
    sanitized_output = "".join(output_with_whitespace.split())
    #Then, strip out all I's, l's, 1's, 0's, O's and punctuation
    #You can't be too careful
    sanitized_output = sanitized_output.replace("I", "").replace("i", "").replace("l", "").replace("1", "")
    sanitized_output = sanitized_output.replace("0", "").replace("O", "")
    sanitized_output = ''.join(filter(str.isalnum, sanitized_output))
    ballot_data["hash"] = hash(sanitized_output)
    return ballot_data


#Scan every single ballot
def ocr_all_ballots(data_directory, savefile):
    #Count the number of files, so we can keep track of progress
    total_number_of_files = 0
    for root, directories, files in os.walk(data_directory):
        for file in files:
            total_number_of_files += 1
    number_of_processed_files = 0

    #Initialize final dictionary of ballots
    ballot_directory = {}
    errors = []
    #Set up directory crawl
    timer_start = time()
    for root, directories, files in os.walk(data_directory):
        for file in files:
            tabulator = int(root.split("/")[5][-5:])
            batch = int(root.split("/")[6][-3:])
            full_file_name = os.path.join(root, file)
            #Get the barcode, or label it as a software error
            try:
                # Create image
                img = capture_third_page(full_file_name)
                ballot_info = read_text(img)
            except:
                ballot_info = "software error"
            try:
                ballot_number = int(file[-6:-4])
                ballot_directory[tabulator][batch][ballot_number] = ballot_info
            except ValueError: #Sometimes the file isn't a ballot file; it might crash the program
                continue
            except KeyError:
                try:
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot_number] = ballot_info
                except KeyError:
                    ballot_directory[tabulator] = {}
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot_number] = ballot_info
            except:
                #Screw it. Just keep going. Don't stop.
                errors.append(full_file_name)
            number_of_processed_files += 1

            # Display updates:
            if number_of_processed_files == 10 or number_of_processed_files == 50 \
                    or number_of_processed_files == 100 or number_of_processed_files % 500 == 0:
                print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                timer = time()
                print(f"Time elapsed (in seconds): {timer - timer_start}")
                save = open(savefile, "w")
                save.write(json.dumps([ballot_directory, errors]))
                save.close()
        save = open(savefile, "w")
        save.write(json.dumps([ballot_directory, errors]))
        save.close()
    return ballot_directory, errors


if __name__ == "__main__":
    path = "/home/dave/Documents/FultonCounty/Tabulator05162/Batch147/Images/05162_00147_000054.tif"
    data_directory, data_has_been_downloaded, browser_type, download_directory = main.load_configuration_information()
    ocr_all_ballots(data_directory, "data/ballot_directory.json")

