import csv


def generate_ballots(filepath="/home/dave/PycharmProjects/FultonCountyBallotScanner/data/LowndesCounty/Lowndes.csv"):
    with open(filepath, errors="replace") as ballot_file:
        fieldnames = ["filename", "tabulator", "batch", "ballot number", "scan time", "scanner", "Poll ID", "Ballot ID",
        "?", "??", "President", "Senate1", "Senate2", "hash"]
        reader = csv.DictReader(ballot_file, fieldnames=fieldnames)
        for row in reader:
            yield row


def create_ballot_directory(filepath="/home/dave/PycharmProjects/FultonCountyBallotScanner/data/LowndesCounty/Lowndes.csv"):
    ballot_generator = generate_ballots(filepath)
    ballot_directory = {}
    for ballot in ballot_generator:
        tabulator = ballot['tabulator']
        batch = ballot['batch']
        ballot_number = ballot['ballot number']
        try:
            ballot_directory[tabulator][batch][ballot_number] = ballot
        except KeyError:
            try:
                ballot_directory[tabulator][batch] = {}
                ballot_directory[tabulator][batch][ballot_number] = ballot
            except KeyError:
                ballot_directory[tabulator] = {}
                ballot_directory[tabulator][batch] = {}
                ballot_directory[tabulator][batch][ballot_number] = ballot

    return ballot_directory

