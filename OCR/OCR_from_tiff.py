import json
from PIL import Image, ImageSequence
import pytesseract
import os
from time import time
from datetime import datetime
from pathlib import Path
from numba import jit



import helper_functions


def capture_third_page(path_to_image):
    image = Image.open(path_to_image)
    page_count = 0
    data_page = None
    for page in ImageSequence.Iterator(image):
        page_count += 1
        if page_count == 3:
            data_page = page
    return data_page


def turn_ocr_text_into_data(ocr_text):
    #Remove all spaces from image for more reliability
    output = ocr_text.replace(" ", "").replace(".", "")
    #Get rid of any accidental double, triple, or quadruple linebreaks
    for i in range(0, 30):
        output = output.replace("\n\n", "\n")

    #Split into lines
    lines = output.split("\n")
    #Create dictionary with all the important attributes of the ballot
    ballot_data = {}

    bookmark1 = lines[0].find("scannedat:")
    bookmark2 = lines[0].find("on")
    ballot_data["filename"] = lines[0][0:bookmark1-3] + "." + lines[0][bookmark1-3:bookmark1]
    # I have no idea why I need to do this, but I do:
    ballot_data["filename"] = ballot_data["filename"].replace("S", "")
    ballot_data["time"] = lines[0][bookmark1+10:bookmark2]
    ballot_data["date"] = lines[0][bookmark2+2:]

    bookmark1 = lines[1].find("Scannedon:")
    bookmark2 = lines[1].find("Tabulator:")
    bookmark3 = lines[1].find("Batch:")
    ballot_data["scanned_on"] = lines[1][bookmark1+10:bookmark2]
    ballot_data["Tabulator"] = lines[1][bookmark2+10:bookmark3]
    ballot_data["Batch"] = lines[1][bookmark3+6:]
    ballot_data["Ballot"] = str(int(ballot_data["filename"][-8:-4]))

    bookmark1 = lines[2].find("PollID:")
    bookmark2 = lines[2].find("BallotID:")
    ballot_data["Poll ID"] = lines[2][bookmark1+7:bookmark2]
    ballot_data["Ballot ID"] = lines[2][bookmark2+9:]

    try: #Assuming that the ballot is a regular, unabridged ballot that displays all races
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
        ballot_data["Adjudicated"] = False
        line_that_starts_adjudication = -1
        for line_index in range(0, len(lines)):
            if "Adjudicatedat" in lines[line_index]:
                ballot_data["Adjudicated"] = True
                line_that_starts_adjudication = line_index
        if ballot_data["Adjudicated"]:
            ballot_data["Adjudication"] = {}
            ballot_data["Adjudication"]['time'] = lines[line_that_starts_adjudication][13:19]
            bookmark1 = lines[line_that_starts_adjudication].find("on")
            bookmark2 = lines[line_that_starts_adjudication].find("by")
            ballot_data["Adjudication"]["date"] = lines[line_that_starts_adjudication][bookmark1+2:bookmark2]
            ballot_data["Adjudication"]["adjudicator"] = lines[line_that_starts_adjudication][bookmark2 + 2:]
            ballot_data["Adjudication"]["President"] = lines[line_that_starts_adjudication + 2][:4]
            ballot_data["Adjudication"]["Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["Special Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["PSC1"] = lines[line_that_starts_adjudication + 6][:4]
            ballot_data["Adjudication"]["PSC2"] = lines[line_that_starts_adjudication + 8][:4]
            ballot_data["Adjudication"]["Race6"] = lines[line_that_starts_adjudication + 10][:6]
            ballot_data["Adjudication"]["Race7"] = lines[line_that_starts_adjudication + 12][:6]
            ballot_data["Adjudication"]["Race8"] = lines[line_that_starts_adjudication + 14][:6]
            ballot_data["Adjudication"]["Race9"] = lines[line_that_starts_adjudication + 16][:6]
            ballot_data["Adjudication"]["Race10"] = lines[line_that_starts_adjudication + 18][:6]
            ballot_data["Adjudication"]["Race11"] = lines[line_that_starts_adjudication + 20][:6]
            ballot_data["Adjudication"]["Race12"] = lines[line_that_starts_adjudication + 22][:6]
            ballot_data["Adjudication"]["Race13"] = lines[line_that_starts_adjudication + 24][:6]
            ballot_data["Adjudication"]["Race14"] = lines[line_that_starts_adjudication + 26][:6]
    except IndexError: #BMD ballots are tricky. Races with no vote are not listed.
        #Assume "Blank Contest" unless a race is specifically listed
        blank_contest = "BLANKC"
        ballot_data["President"] = blank_contest
        ballot_data["Senate"] = blank_contest
        ballot_data["Special Senate"] = blank_contest
        ballot_data["PSC1"] = blank_contest
        ballot_data["PSC2"] = blank_contest
        ballot_data["Race6"] = blank_contest
        ballot_data["Race7"] = blank_contest
        ballot_data["Race8"] = blank_contest
        ballot_data["Race9"] = blank_contest
        ballot_data["Race10"] = blank_contest
        ballot_data["Race11"] = blank_contest
        ballot_data["Race12"] = blank_contest
        ballot_data["Race13"] = blank_contest
        ballot_data["Race14"] = blank_contest
        ballot_data["Adjudicated"] = False
        for line_index in range(0, len(lines)):
            if "President" in lines[line_index]:
                ballot_data["President"] = lines[line_index + 1][:4]
            elif "Perdue" in lines[line_index]:
                ballot_data["Senate"] = lines[line_index + 1][:4]
            elif "Loeffler" in lines[line_index]:
                ballot_data["Special Senate"] = lines[line_index + 1][:4]
            elif "CommissionDistrict1" in lines[line_index]:
                ballot_data["PSC1"] = lines[line_index + 1][:4]
            elif "CommissionDistrict4" in lines[line_index]:
                ballot_data["PSC2"] = lines[line_index + 1][:4]
            elif "HouseDistrict" in lines[line_index]:
                ballot_data["Race6"] = lines[line_index + 1][:6]
            elif "StateSenateDistrict" in lines[line_index]:
                ballot_data["Race7"] = lines[line_index + 1][:6]
            elif "StateHouseDistrict" in lines[line_index]:
                ballot_data["Race8"] = lines[line_index + 1][:6]
            elif "DistrictAttorney" in lines[line_index]:
                ballot_data["Race9"] = lines[line_index + 1][:6]
            elif "SuperiorCourt" in lines[line_index]:
                ballot_data["Race10"] = lines[line_index + 1][:6]
            elif "Sheriff" in lines[line_index]:
                ballot_data["Race11"] = lines[line_index + 1][:6]
            elif "TaxCommissioner" in lines[line_index]:
                ballot_data["Race12"] = lines[line_index + 1][:6]
            elif "Surveyor" in lines[line_index]:
                ballot_data["Race13"] = lines[line_index + 1][:6]
            elif "SolicitorGeneral" in lines[line_index]:
                ballot_data["Race14"] = lines[line_index + 1][:6]

    #Create a single hash to represent the complete, maximally unique data on the entire ballot
    #First, strip all whitespace for maximum reliability
    sanitized_output = "".join(output.split())
    #Next, strip out all text after the words "Adjudicated at ..." to prevent adjudication from spoiling matches
    bookmark1 = sanitized_output.find("Adjudicatedat")
    sanitized_output = sanitized_output[0:bookmark1]
    #Next, strip out the first two lines to get rid of filename info and datetime info
    bookmark2 = sanitized_output.find("Batch")
    sanitized_output = sanitized_output[bookmark2+9:]
    #Then, strip out all I's, l's, 1's, 0's, O's and punctuation
    #You can't be too careful
    sanitized_output = sanitized_output.replace("I", "").replace("i", "").replace("l", "").replace("1", "")
    sanitized_output = sanitized_output.replace("0", "").replace("O", "")
    sanitized_output = ''.join(filter(str.isalnum, sanitized_output))
    ballot_data["hash"] = hash(sanitized_output)
    return ballot_data


def read_text(image_with_data):
    #Read text with image
    output_with_whitespace = pytesseract.image_to_string(image_with_data)
    #Remove all spaces from image for more reliability
    output = output_with_whitespace.replace(" ", "").replace(".", "")
    #Get rid of any accidental double, triple, or quadruple linebreaks
    for i in range(0, 30):
        output = output.replace("\n\n", "\n")

    #Split into lines
    lines = output.split("\n")
    #Create dictionary with all the important attributes of the ballot
    ballot_data = {}

    bookmark1 = lines[0].find("scannedat:")
    bookmark2 = lines[0].find("on")
    ballot_data["filename"] = lines[0][0:bookmark1-3] + "." + lines[0][bookmark1-3:bookmark1]
    # I have no idea why I need to do this, but I do:
    ballot_data["filename"] = ballot_data["filename"].replace("S", "")
    ballot_data["time"] = lines[0][bookmark1+10:bookmark2]
    ballot_data["date"] = lines[0][bookmark2+2:]

    bookmark1 = lines[1].find("Scannedon:")
    bookmark2 = lines[1].find("Tabulator:")
    bookmark3 = lines[1].find("Batch:")
    ballot_data["scanned_on"] = lines[1][bookmark1+10:bookmark2]
    ballot_data["Tabulator"] = lines[1][bookmark2+10:bookmark3]
    ballot_data["Batch"] = lines[1][bookmark3+6:]
    ballot_data["Ballot"] = str(int(ballot_data["filename"][-8:-4]))

    bookmark1 = lines[2].find("PollID:")
    bookmark2 = lines[2].find("BallotID:")
    ballot_data["Poll ID"] = lines[2][bookmark1+7:bookmark2]
    ballot_data["Ballot ID"] = lines[2][bookmark2+9:]

    try: #Assuming that the ballot is a regular, unabridged ballot that displays all races
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
        ballot_data["Adjudicated"] = False
        line_that_starts_adjudication = -1
        for line_index in range(0, len(lines)):
            if "Adjudicatedat" in lines[line_index]:
                ballot_data["Adjudicated"] = True
                line_that_starts_adjudication = line_index
        if ballot_data["Adjudicated"]:
            ballot_data["Adjudication"] = {}
            ballot_data["Adjudication"]['time'] = lines[line_that_starts_adjudication][13:19]
            bookmark1 = lines[line_that_starts_adjudication].find("on")
            bookmark2 = lines[line_that_starts_adjudication].find("by")
            ballot_data["Adjudication"]["date"] = lines[line_that_starts_adjudication][bookmark1+2:bookmark2]
            ballot_data["Adjudication"]["adjudicator"] = lines[line_that_starts_adjudication][bookmark2 + 2:]
            ballot_data["Adjudication"]["President"] = lines[line_that_starts_adjudication + 2][:4]
            ballot_data["Adjudication"]["Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["Special Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["PSC1"] = lines[line_that_starts_adjudication + 6][:4]
            ballot_data["Adjudication"]["PSC2"] = lines[line_that_starts_adjudication + 8][:4]
            ballot_data["Adjudication"]["Race6"] = lines[line_that_starts_adjudication + 10][:6]
            ballot_data["Adjudication"]["Race7"] = lines[line_that_starts_adjudication + 12][:6]
            ballot_data["Adjudication"]["Race8"] = lines[line_that_starts_adjudication + 14][:6]
            ballot_data["Adjudication"]["Race9"] = lines[line_that_starts_adjudication + 16][:6]
            ballot_data["Adjudication"]["Race10"] = lines[line_that_starts_adjudication + 18][:6]
            ballot_data["Adjudication"]["Race11"] = lines[line_that_starts_adjudication + 20][:6]
            ballot_data["Adjudication"]["Race12"] = lines[line_that_starts_adjudication + 22][:6]
            ballot_data["Adjudication"]["Race13"] = lines[line_that_starts_adjudication + 24][:6]
            ballot_data["Adjudication"]["Race14"] = lines[line_that_starts_adjudication + 26][:6]
    except IndexError: #BMD ballots are tricky. Races with no vote are not listed.
        #Assume "Blank Contest" unless a race is specifically listed
        blank_contest = "BLANKC"
        ballot_data["President"] = blank_contest
        ballot_data["Senate"] = blank_contest
        ballot_data["Special Senate"] = blank_contest
        ballot_data["PSC1"] = blank_contest
        ballot_data["PSC2"] = blank_contest
        ballot_data["Race6"] = blank_contest
        ballot_data["Race7"] = blank_contest
        ballot_data["Race8"] = blank_contest
        ballot_data["Race9"] = blank_contest
        ballot_data["Race10"] = blank_contest
        ballot_data["Race11"] = blank_contest
        ballot_data["Race12"] = blank_contest
        ballot_data["Race13"] = blank_contest
        ballot_data["Race14"] = blank_contest
        ballot_data["Adjudicated"] = False
        for line_index in range(0, len(lines)):
            if "President" in lines[line_index]:
                ballot_data["President"] = lines[line_index + 1][:4]
            elif "Perdue" in lines[line_index]:
                ballot_data["Senate"] = lines[line_index + 1][:4]
            elif "Loeffler" in lines[line_index]:
                ballot_data["Special Senate"] = lines[line_index + 1][:4]
            elif "CommissionDistrict1" in lines[line_index]:
                ballot_data["PSC1"] = lines[line_index + 1][:4]
            elif "CommissionDistrict4" in lines[line_index]:
                ballot_data["PSC2"] = lines[line_index + 1][:4]
            elif "HouseDistrict" in lines[line_index]:
                ballot_data["Race6"] = lines[line_index + 1][:6]
            elif "StateSenateDistrict" in lines[line_index]:
                ballot_data["Race7"] = lines[line_index + 1][:6]
            elif "StateHouseDistrict" in lines[line_index]:
                ballot_data["Race8"] = lines[line_index + 1][:6]
            elif "DistrictAttorney" in lines[line_index]:
                ballot_data["Race9"] = lines[line_index + 1][:6]
            elif "SuperiorCourt" in lines[line_index]:
                ballot_data["Race10"] = lines[line_index + 1][:6]
            elif "Sheriff" in lines[line_index]:
                ballot_data["Race11"] = lines[line_index + 1][:6]
            elif "TaxCommissioner" in lines[line_index]:
                ballot_data["Race12"] = lines[line_index + 1][:6]
            elif "Surveyor" in lines[line_index]:
                ballot_data["Race13"] = lines[line_index + 1][:6]
            elif "SolicitorGeneral" in lines[line_index]:
                ballot_data["Race14"] = lines[line_index + 1][:6]

    #Create a single hash to represent the complete, maximally unique data on the entire ballot
    #First, strip all whitespace for maximum reliability
    sanitized_output = "".join(output_with_whitespace.split())
    #Next, strip out all text after the words "Adjudicated at ..." to prevent adjudication from spoiling matches
    bookmark1 = sanitized_output.find("Adjudicatedat")
    sanitized_output = sanitized_output[0:bookmark1]
    #Next, strip out the first two lines to get rid of filename info and datetime info
    bookmark2 = sanitized_output.find("Batch")
    sanitized_output = sanitized_output[bookmark2+9:]
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


#Scan every single ballot from ocr text files
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
                ballot_info = turn_ocr_text_into_data(ocr_text)
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
                save = open(savefile, "w")
                save.write(json.dumps([ballot_directory, errors]))
                save.close()
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


if __name__ == "__main__":
    bd = "/home/dave/Documents/Election Fraud/Fulton Recount Ballot Images"
    od = "/home/dave/Documents/Election Fraud/Fulton_Recount_OCR2"
    create_ocr_textfiles(bd, od)