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
            #Create image
            img = Image.open(full_file_name)
            #Turn image into numpy array
            image_data = np.asarray(img)
            #Get the barcode, or label it as a software error
            try:
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


if __name__ == "__main__":
    data_directory, data_has_been_downloaded, browser_type, download_directory = main.load_configuration_information()
    barcodes = scan_all_barcodes(data_directory)
    save_file = open("barcodes.json",'w')
    save_file.write(json.dumps(barcodes))
    save_file.close()
    print(barcodes)