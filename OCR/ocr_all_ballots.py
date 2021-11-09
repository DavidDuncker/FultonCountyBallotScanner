import json
import os
from datetime import datetime
from time import time

from OCR.capture_third_page import capture_third_page
from OCR.read_text import read_text


def ocr_all_ballots(data_directory, savefile):
    #Count the number of files, so we can keep track of progress
    total_number_of_files = 0
    for root, directories, files in os.walk(data_directory):
        for file in files:
            if ".tif" in file:
                total_number_of_files += 1
    number_of_processed_files = 0

    #Initialize final dictionary of ballots
    ballot_directory = {}
    errors = []
    #Set up directory crawl
    timer_start = time()
    print(f"Starting datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}")
    for root, directories, files in os.walk(data_directory):
        for file in files:
            if ".tif" not in file:
                continue
            tabulator = int(root.split("/")[5][-5:])
            batch = int(root.split("/")[6][-3:])
            full_file_name = os.path.join(root, file)
            #Get the barcode, or label it as a software error
            try:
                # Create image
                img = capture_third_page(full_file_name)
                ballot_info = read_text(img)
                img.close()
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
            if number_of_processed_files == 10 or number_of_processed_files == 50 \
                    or number_of_processed_files == 100 or number_of_processed_files % 500 == 0:
                print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                timer = time()
                print(f"Time elapsed (in seconds): {timer - timer_start}")
                print(f"Milestone datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}\n\n")
                save = open(savefile, "w")
                save.write(json.dumps([ballot_directory, errors]))
                save.close()
        save = open(savefile, "w")
        save.write(json.dumps([ballot_directory, errors]))
        save.close()
    return [ballot_directory, errors]