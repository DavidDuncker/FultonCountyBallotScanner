import read_csv_data
import generate_list_of_races
import turn_third_page_into_data
import json


def get_ballot_data(ballot, list_of_races):
    ballot_data = turn_third_page_into_data.read_text(ballot["lastpage"], list_of_races)
    ballot_data['filename'] = ballot['filepath'].split("/")[-1]
    ballot_data['time'] = ballot['modified'].split(" ")[1]
    ballot_data['date'] = ballot['modified'].split(" ")[0]
    ballot_data['scanned_on'] = ballot['scannedon']
    ballot_data['Tabulator'] = ballot['Tabulator']
    ballot_data['Batch'] = ballot['Batch']
    ballot_data['Ballot'] = ballot['Ballot']
    return ballot_data


def get_ballot_directory(json_save_path):
    csv_path = "douglas-ocr-rev2.csv"
    csv_data = read_csv_data.read_douglas_county_csv_file(csv_path)
    ballot_generator = generate_list_of_races.ballot_generator_douglas_county(csv_data)
    list_of_races = generate_list_of_races.get_all_races(ballot_generator)

    ballot_directory = {}
    ballot_generator = generate_list_of_races.ballot_generator_douglas_county(csv_data)
    for ballot in ballot_generator:
        ballot_data = get_ballot_data(ballot, list_of_races)
        tabulator = ballot_data['Tabulator']
        batch = ballot_data['Batch']
        ballot_number = ballot_data["Ballot"]
        try:
            ballot_directory[tabulator][batch][ballot_number] = ballot_data
        except KeyError:
            try:
                ballot_directory[tabulator][batch] = {}
                ballot_directory[tabulator][batch][ballot_number] = ballot_data
            except KeyError:
                ballot_directory[tabulator] = {}
                ballot_directory[tabulator][batch] = {}
                ballot_directory[tabulator][batch][ballot_number] = ballot_data

    json_savefile = open(json_save_path, 'w')
    json_savefile.write(json.dumps(ballot_directory))
    json_savefile.close()

    return ballot_directory


if __name__ == "__main__":
    ballot_directory = get_ballot_directory("ballot_directory.json")
