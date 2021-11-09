import sqlite3
from compile_ballot_data import generate_list_of_races
from collections import defaultdict
from helper_functions import post_updates, recursively_de_infinitize_dictionary
from OCR.transform_ocr_text import turn_ocr_text_into_hash_with_first_2_letters_of_each_line as transcribe

def get_a_single_ballot():
    ocr_filepath = "/home/dave/Documents/Election Fraud/Fulton_Recount_OCR/recount.sql3"

    #Connect to database
    connection = sqlite3.connect(ocr_filepath)
    cursor = connection.cursor()
    statement = "SELECT * FROM ballot_ocr;"
    cursor.execute(statement)
    rows = cursor.fetchall()
    for row in rows:
        #Return current ballot info
        yield row[1]


def create_ballot_directory():
    ballot_generator = get_a_single_ballot()
    infinite_dictionary = lambda: defaultdict(infinite_dictionary)
    ballot_directory = infinite_dictionary()

    count = 0
    for [filename, third_page_data] in ballot_generator:
        filename = filename.split(".")[0]
        tabulator = str(int(filename.split("_")[0]))
        batch = str(int(filename.split("_")[1]))
        ballot_number = str(int(filename.split("_")[2]))
        ballot_directory[tabulator][batch][ballot_number] = transcribe(third_page_data)
        count +=1
        post_updates(count, [100, 1000, 10000, 50000, 100000])

    ballot_directory = recursively_de_infinitize_dictionary(ballot_directory)

    return ballot_directory


def get_all_races():
    ballots = get_a_single_ballot()
    list_of_races = generate_list_of_races.get_all_races(ballots)
    return list_of_races


if __name__ == "__main__":
    ballots = get_a_single_ballot()
    for i in range(0, 100):
        print(next(ballots))