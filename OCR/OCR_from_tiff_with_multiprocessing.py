import json
from PIL import Image, ImageSequence
import pytesseract
import os
from time import time
from datetime import datetime
from pathlib import Path
from multiprocessing import Process


def capture_third_page(path_to_image):
    image = Image.open(path_to_image)
    page_count = 0
    data_page = None
    for page in ImageSequence.Iterator(image):
        page_count += 1
        if page_count == 3:
            data_page = page
    return data_page


def capture_and_write(root, file, ballot_directory, ocr_directory):
    #root = args[0]
    #file = args[1]
    #ballot_directory = args[2]
    #ocr_directory = args[3]
    ballot_filepath = os.path.join(root, file)
    img = capture_third_page(ballot_filepath)
    print("Starting OCR")
    ocr_string = pytesseract.image_to_string(img, lang="eng")
    print("Got OCR")
    new_path = root[len(ballot_directory)+1:]
    new_ocr_path = os.path.join(ocr_directory, new_path)
    Path(new_ocr_path).mkdir(parents=True, exist_ok=True)
    ocr_filename = file[0:-4] + ".ocr"
    ocr_filepath = os.path.join(new_ocr_path, ocr_filename)
    ocr_file = open(ocr_filepath, 'w')
    ocr_file.write(ocr_string)
    ocr_file.close()


def do_tasks(processes):
    pool_workers = []
    for core in processes:
        for task in core:
            if task != None:
                pool_workers.append(Process(target=capture_and_write, args=task))

    print("Starting tasks")
    for worker in pool_workers:
        worker.start()
    print("Waiting for tasks to finish")
    for worker in pool_workers:
        worker.join()


def reset_processes(number_of_cores, num_of_tasks_per_core):
    processes = [[] for x in range(0, number_of_cores)]
    for process in range(0, len(processes)):
        processes[process] = [None for x in range(0, num_of_tasks_per_core)]

    return processes


def create_ocr_textfiles(ballot_directory, ocr_directory, number_of_cores, num_of_tasks_per_core):
    #Count the number of files, so we can keep track of progress
    #Also, create new directories if needed
    print("Getting number of files")
    total_number_of_files = 0
    for root, directories, files in os.walk(ballot_directory):
        for file in files:
            if ".tif" in file:
                total_number_of_files += 1
    number_of_processed_files = 0

    #Set up a list of processes
    processes = reset_processes(number_of_cores, num_of_tasks_per_core)
    current_core = 0
    current_task = 0


    #Set up directory crawl
    timer_start = time()
    print(f"Starting datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}")

    for root, directories, files in os.walk(ballot_directory):
        for file in files:
            if ".tif" not in file:
                continue

            arguments = [root, file, ballot_directory, ocr_directory]
            processes[current_core][current_task] = arguments
            current_task += 1
            if current_task == num_of_tasks_per_core:
                current_task = 0
                current_core += 1
                if current_core == number_of_cores:
                    current_core = 0
                    do_tasks(processes)
                    processes = reset_processes(number_of_cores, num_of_tasks_per_core)
                    number_of_processed_files += number_of_cores * num_of_tasks_per_core

                # Display updates:
                if number_of_processed_files == number_of_cores*1 or number_of_processed_files == number_of_cores*2 \
                        or number_of_processed_files == number_of_cores*3 or \
                        number_of_processed_files % (2*number_of_cores) == 0:
                    print(f"Progress: {number_of_processed_files}/{total_number_of_files}")
                    timer = time()
                    print(f"Time elapsed (in seconds): {timer - timer_start}")
                    print(f"Milestone datetime: {datetime.now().strftime('%H:%M:%S %m/%d/%Y')}\n\n")

    #Finish up the last few tasks:
    do_tasks(processes)


if __name__ == "__main__":
    bd = "/home/dave/Documents/Election Fraud/Fulton Recount Ballot Images"
    od = "/home/dave/Documents/Election Fraud/Fulton_Recount_OCR2"
    create_ocr_textfiles(bd, od, 4, 4)