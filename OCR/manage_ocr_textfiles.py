import json
import os
from datetime import datetime
from pathlib import Path
from time import time

import pytesseract

from OCR.capture_third_page import capture_third_page
from OCR.transform_ocr_text import turn_ocr_text_into_data
from OCR.transform_ocr_text import turn_ocr_text_into_hash_with_first_2_letters_of_each_line


def load_all_ocr_texts(directory, savefile):
    #Count the number of files, so we can keep track of progress
    total_number_of_files = 0
    for root, directories, files in os.walk(directory):
        for file in files:
            total_number_of_files += 1
    number_of_processed_files = 0

    #Initialize final dictionary of ballots
    ballot_directory = {}
    errors = []
    #Set up directory crawl
    timer_start = time()
    print(f"Starting datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}")
    for root, directories, files in os.walk(directory):
        for file in files:
            if ".ocr" not in file:
                continue
            tabulator = int(file.split("_")[0][-5:])
            batch = int(file.split("_")[1][-3:])
            full_file_name = os.path.join(root, file)
            #Open and read OCR file
            ocr_file = open(full_file_name, 'r')
            ocr_text = ocr_file.read()
            ocr_file.close()
            #Get the barcode, or label it as a software error
            try:
                #Capture ballot info
                #ballot_info = turn_ocr_text_into_data(ocr_text)
                ballot_info = turn_ocr_text_into_hash_with_first_2_letters_of_each_line(ocr_text)
                ballot_info["filename"] = file[:-4] + ".tif"
            except:
                ballot_info = "software error"
                errors.append(f"{tabulator}/{batch}/{file[-8:-4]}")
                continue
            try:
                ballot_number = int(file[-8:-4])
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
            if number_of_processed_files == 100 or number_of_processed_files == 500 \
                    or number_of_processed_files == 1000 or number_of_processed_files % 20000 == 0:
                print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                timer = time()
                print(f"Time elapsed (in seconds): {timer - timer_start}")
                print(f"Milestone datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}\n\n")
                #save = open(savefile, "w")
                #save.write(json.dumps([ballot_directory, errors]))
                #save.close()
        save = open(savefile, "w")
        save.write(json.dumps([ballot_directory, errors]))
        save.close()
    return [ballot_directory, errors]


def create_ocr_textfiles(ballot_directory, ocr_directory):
    #Count the number of files, so we can keep track of progress
    #Also, create new directories if needed
    print("Getting number of files")
    total_number_of_files = 0
    for root, directories, files in os.walk(ballot_directory):
        for file in files:
            if ".tif" in file:
                total_number_of_files += 1
    number_of_processed_files = 0

    #Set up directory crawl
    timer_start = time()
    print(f"Starting datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}")

    for root, directories, files in os.walk(ballot_directory):
        for file in files:
            if ".tif" not in file:
                continue

            ballot_filepath = os.path.join(root, file)
            img = capture_third_page(ballot_filepath)
            ocr_string = pytesseract.image_to_string(img, lang="eng", config="--psm 11")
            new_path = root[len(ballot_directory) + 1:]
            new_ocr_path = os.path.join(ocr_directory, new_path)
            Path(new_ocr_path).mkdir(parents=True, exist_ok=True)
            ocr_filename = file[0:-4] + ".ocr"
            ocr_filepath = os.path.join(new_ocr_path, ocr_filename)
            ocr_file = open(ocr_filepath, 'w')
            ocr_file.write(ocr_string)
            ocr_file.close()

            number_of_processed_files += 1

            # Display updates:
            if number_of_processed_files == 1 or number_of_processed_files == 10 \
                    or number_of_processed_files == 100 or \
                    number_of_processed_files % 500 == 0:
                print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                timer = time()
                print(f"Time elapsed (in seconds): {timer - timer_start}")
                print(f"Milestone datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}\n\n")