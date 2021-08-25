#Abandoned; the data in HG's SQL file is much better than the OCR from ballots.youpeople

import os


def get_files(directory):
    list_of_ocr_files = []
    for root, directories, files in os.walk(directory):
        for file in files:
            if "ocr.Tabulator" in file:
                path = os.path.join(root, file)
                list_of_ocr_files.append(path)

    return list_of_ocr_files


if __name__ == "__main__":
    ocr_directory = "/home/dave/Documents/Election Fraud/Fulton_Recount_OCR/"
    list = get_files(ocr_directory)
    for filepath in list:
        file = open(filepath, 'r')
        data = file.read()
        file.close()
        data_rows = data.split("\n")