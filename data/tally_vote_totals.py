import csv
import os
from tally_data import tally_data_by_batch


def create_ballot_dict(path):
    with open(path) as csv_file:
        ballot_directory = {}
        field_names = ["filename", "tabulator", "batch", "ballot", "BMD", "adjudicated",
                       "Last Write Time Utc", "scan_time",
                       "scanner", "Poll ID", "Ballot ID", "Combo", "Precinct", "President", "senate1", "senate2",
                       "hash"]
        csv_file.__next__()
        reader = csv.DictReader(csv_file, fieldnames=field_names)
        for row in reader:
            tabulator = row["tabulator"]
            batch = row["batch"]
            ballot = row["ballot"]
            try:
                ballot_directory[tabulator][batch][ballot] = row
            except KeyError:
                try:
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot] = row
                except KeyError:
                    ballot_directory[tabulator] = {}
                    ballot_directory[tabulator][batch] = {}
                    ballot_directory[tabulator][batch][ballot] = row

    return ballot_directory


def tally_totals(path):
    ballot_directory = create_ballot_dict(path)
    tally_of_data = tally_data_by_batch.get_tally_of_ballot_info(ballot_directory, ["President", "senate1", "senate2", "adjudicated"])
    for race in tally_of_data['total'].keys():
        print(f"{race}:")
        for (candidate, vote_count) in tally_of_data['total'][race].items():
            print(f"\t{candidate}:\t{vote_count}")


if __name__ == "__main__":
    path = "/home/dave/Documents/Election Fraud/Ballot images/downloads_9_15"
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".csv" in file:
                path_to_ocr = os.path.join(root, file)
                print(f"{file}:")
                tally_totals(path_to_ocr)
                print("\n\n")
