import tally_data_by_batch as t
import json


if __name__ == "__main__":
    tally = t.get_tally_of_ballot_info("../data/ballot_directory.json")

    for q in tally['total']['hash'].keys():
        if tally['total']['hash'][q] > 200:
            print(f"{q}:\t{tally['total']['hash'][q]}")

    b = open("/home/dave/PycharmProjects/FultonCountyBallotScanner/data/ballot_directory.json", 'r')
    ballots = json.loads(b.read())
    b.close()

    for t in ballots[0].keys():
        for bt in ballots[0][t].keys():
            for bl in ballots[0][t][bt].keys():
                try:
                    if ballots[0][t][bt][bl]["hash"] == -5340025583637180108:
                        pass
                        print(ballots[0][t][bt][bl])
                except:
                    continue

