import csv


def read_douglas_county_csv_file(path):
    csv_dict = {}
    with open(path) as csv_file:
        ballot_reader = csv. reader(csv_file, delimiter=",")
        columns = next(ballot_reader)
        for row in ballot_reader:
            tabulator = row[1].split("/")[-1].split("_")[0]
            tabulator = str(int(tabulator))

            batch = row[1].split("/")[-1].split("_")[1]
            batch = str(int(batch))

            ballot_number = row[1].split("/")[-1].split("_")[2][-10:-4]
            ballot_number = str(int(ballot_number))

            ballot_dict = {columns[i]: row[i] for i in range(0, len(row))}

            try:
                csv_dict[tabulator][batch][ballot_number] = ballot_dict
            except KeyError:
                try:
                    csv_dict[tabulator][batch] = {}
                    csv_dict[tabulator][batch][ballot_number] = ballot_dict
                except KeyError:
                    csv_dict[tabulator] = {}
                    csv_dict[tabulator][batch] = {}
                    csv_dict[tabulator][batch][ballot_number] = ballot_dict

    return csv_dict


if __name__ == "__main__":
    csv_path = "/data/DouglasCounty/douglas-ocr-rev2.csv"
    ballot_data = read_douglas_county_csv_file(csv_path)


