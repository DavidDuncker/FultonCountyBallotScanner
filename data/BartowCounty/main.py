import csv
import json


def create_ballot_dict(path="/home/dave/PycharmProjects/FultonCountyBallotScanner/data/BartowCounty/bartow_ballots.csv",
                       savefile="/home/dave/PycharmProjects/FultonCountyBallotScanner/data/BartowCounty/"
                                "ballot_directory.json"):
    with open(path) as csv_file:
        ballot_directory = {}
        field_names = ["filename", "tabulator" ,"batch", "ballot", "scan_time", "scanner", "Ballot ID", "Poll ID",
                       "President", "senate1", "senate2","hash"]
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

    f = open(savefile, 'w')
    f.write(json.dumps(ballot_directory))
    f.close()

    return ballot_directory

if __name__ == "__main__":
    path = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/BartowCounty/bartow_ballots.csv"
