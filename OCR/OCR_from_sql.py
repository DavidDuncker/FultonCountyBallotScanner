import sqlite3
from OCR import generate_list_of_races
from collections import Counter

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
        yield row


def get_all_races():
    ballots = get_a_single_ballot()
    list_of_races = generate_list_of_races.get_all_races(ballots)
    return list_of_races

if __name__ == "__main__":
    ballots = get_a_single_ballot()
    for i in range(0, 100):
        print(next(ballots))