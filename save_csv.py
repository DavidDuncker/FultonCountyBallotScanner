import csv
import json


def create_csv_file(csv_file_path, rolling_average_file_path, tabulator):
    csv_file = open(csv_file_path, 'w')
    csv_writer = csv.writer(csv_file)

    rolling_average_file = open(rolling_average_file_path, 'r')
    rolling_average = json.loads(rolling_average_file.read())
    rolling_average_file.close()

    header = []
    for column in rolling_average[tabulator].keys():
        header.append(column)

    rows = []
    number_of_rows = len(rolling_average["All"]["time"])
    for row_index in range(0, number_of_rows):
        row = []
        for column in rolling_average[tabulator].keys():
            row.append(rolling_average[tabulator][column][row_index])
        rows.append(row)

    csv_writer.writerow(header)
    csv_writer.writerows(rows)
    csv_file.close()


if __name__ == "__main__":
    csv_file_path = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/csv/timeseries.csv"
    rolling_average_file_path = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/rolling_average_500.json"
    tabulator = "All"
    create_csv_file(csv_file_path, rolling_average_file_path, tabulator)