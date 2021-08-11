from timeseries_and_rolling_averages import create_ordered_timeseries_of_ballots
from collections import Counter
#I'm having trouble finding some way to figure out how to detect multiple passes of the same ballot.
#I decided that if poll workers were scanning and re-scanning ballots over and over again, then the
#"average distance to the next identical ballot" should be relatively close to one
#and the distribution of distances to the next identical ballot should have a spike at the number 1

#Let's hope for the best.


if __name__ == "__main__":
    print("Getting timeseries")
    timeseries = create_ordered_timeseries_of_ballots("/home/dave/PycharmProjects/FultonCountyBallotScanner/data/ballot_directory_backup.json")
    distances = "" #Making it a string to see as much of the data as possible
    distances_l = []
    print("Getting distances")
    for tabulator in timeseries:
        print(f"Tabulator: {tabulator}")
        for i in range(0, len(timeseries[tabulator])):
            distance = -1
            for j in range(i+1, len(timeseries[tabulator])):
                try:
                    if timeseries[tabulator][i]["hash"] == timeseries[tabulator][j]["hash"]:
                        distance = j - i
                except TypeError:
                    continue
            distances += str(distance) + ", "
            if len(distances) % 400 == 0:
                distances += "\n"
            distances_l.append(distance)

            if i % 1000 == 0:
                print(f"Ballot: {i}")

            if i == 2000:
                break

        print(f"{tabulator}: {Counter(distances_l)}")



