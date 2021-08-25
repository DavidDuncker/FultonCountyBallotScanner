import OCR.OCR_from_sql
import OCR.turn_OCR_into_data
import sqlite3
from data.DouglasCounty import generate_list_of_races


def add_to_ballot_dict(ballot_dict, ballot_data):
    tabulator = ballot_data["Tabulator"]
    batch = ballot_data["Batch"]
    ballot_number = ballot_data["Ballot"]
    try:
        ballot_dict[tabulator][batch][ballot_number] = ballot_data
    except KeyError:
        try:
            ballot_dict[tabulator][batch] = {}
            ballot_dict[tabulator][batch][ballot_number] = ballot_data
        except KeyError:
            try:
                ballot_dict[tabulator] = {}
                ballot_dict[tabulator][batch] = {}
                ballot_dict[tabulator][batch][ballot_number] = ballot_data
            except KeyError:
                ballot_dict = {}
                ballot_dict[tabulator] = {}
                ballot_dict[tabulator][batch] = {}
                ballot_dict[tabulator][batch][ballot_number] = ballot_data
    return ballot_dict


def get_ballots_from_sql():
    ocr_filepath = "/home/dave/Documents/Election Fraud/Fulton_Recount_OCR/recount.sql3"

    connection = sqlite3.connect(ocr_filepath)
    cursor = connection.cursor()
    statement = "SELECT * FROM ballot_ocr;"
    cursor.execute(statement)
    ballots = cursor.fetchall()

    return ballots


def create_ballot_dictionary(ballot_generator):
    print("Getting list of races")
    list_of_races = generate_list_of_races.get_all_races(ballot_generator)

    ballot_dict = {}

    ballots = get_ballots_from_sql()

    number_of_ballots_processed = 0
    alert_index = 0
    alert_list = [1, 10, 100, 500, 1000]
    for ballot in ballots:
        #print(ballot[0])
        ballot_data = OCR.turn_OCR_into_data.read_text(ballot[1], list_of_races)
        ballot_dict = add_to_ballot_dict(ballot_dict, ballot_data)

        number_of_ballots_processed += 1
        alert_number = alert_list[alert_index]
        if number_of_ballots_processed % alert_number == 0:
            print(f"Number of ballots processed: {number_of_ballots_processed}\n")
            if alert_index < len(alert_list)-1:
                alert_index += 1

    return ballot_dict


if __name__ == "__main__":
    pass