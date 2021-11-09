import csv
from helper_functions import post_updates

def print_interesting_datapoint(eba_filepath):
    number = 0
    list_of_a_reg = []
    list_of_good_returned = []
    with open(eba_filepath, errors="replace") as eba_file:
        reader = csv.DictReader(eba_file)
        for row in reader:
            #election = row["Election Name"]
            #if election == 'GENERAL/SPECIAL ELECTION':
            #    pass
            #election_date = row['Election Date']
            #if election_date != "11/03/2020":
            #    continue
            #county = row['County']
            #if county != "FULTON":
            #    continue
            #return_date = row["BallotReturn Date"]
            #ballot_style = row["Ballot Style"]
            #status_reason = row["Status Reason"]
            #municipal_precinct = row["Municipal Precinct"]
            #county_precinct = row["County Precinct"]
            #application_status = row["Application Status"]
            #ballot_status = row["Ballot Status"]
            #city = row['City']
            #registration_number = row['Voter Registration']
            registration_number = row['Voter Registration #']
            #id = row["ID"]
            number += 1
            if int(registration_number) == 10860935:
                print(row)
            #post_updates(number, [1, 10, 100, 1000, 10000, 100000])

    return True


def get_absentee_timeseries(eba_filepath):
    absentee_counts_by_ballot_style = {}
    absentee_counts_by_precinct = {}
    date_timeseries = {}
    with open(eba_filepath) as eba_file:
        reader = csv.DictReader(eba_file)
        for row in reader:
            election = row["Election Name"]
            if election == 'GENERAL/SPECIAL ELECTION':
                pass
            election_date = row['Election Date']
            if election_date != "11/03/2020":
                continue
            county = row['County']
            if county != "FULTON":
                continue
            return_date = row["BallotReturn Date"]
            if len(return_date) < 3:
                return_date = "No Return Date Listed"
            ballot_style = row["Ballot Style"]
            municipal_precinct = row["Municipal Precinct"]
            county_precinct = row["County Precinct"]

            try:
                absentee_counts_by_ballot_style[ballot_style][county_precinct] += 1
            except KeyError:
                try:
                    absentee_counts_by_ballot_style[ballot_style][county_precinct] = 1
                except KeyError:
                    absentee_counts_by_ballot_style[ballot_style] = {}
                    absentee_counts_by_ballot_style[ballot_style][county_precinct] = 1

            try:
                absentee_counts_by_ballot_style[ballot_style]["all precincts"] += 1
            except KeyError:
                absentee_counts_by_ballot_style[ballot_style]["all precincts"] = 1

            try:
                absentee_counts_by_precinct[county_precinct][ballot_style] += 1
            except KeyError:
                try:
                    absentee_counts_by_precinct[county_precinct][ballot_style] = 1
                except KeyError:
                    absentee_counts_by_precinct[county_precinct] = {}
                    absentee_counts_by_precinct[county_precinct][ballot_style] = 1

            try:
                absentee_counts_by_precinct[county_precinct]["all ballot styles"] += 1
            except KeyError:
                absentee_counts_by_precinct[county_precinct]["all ballot styles"] = 1


            try:
                date_timeseries[county_precinct][return_date] += 1
            except KeyError:
                try:
                    date_timeseries[county_precinct][return_date] = 1
                except KeyError:
                    date_timeseries[county_precinct] = {}
                    date_timeseries[county_precinct][return_date] = 1

    return absentee_counts_by_ballot_style, absentee_counts_by_precinct, date_timeseries


def create_csv(date_timeseries, csv_filepath):
    with open(csv_filepath, 'w', newline='') as csvfile:
        precincts = list(date_timeseries.keys())
        dates = []
        for precinct in precincts:
            for date in date_timeseries[precinct].keys():
                if date not in dates:
                    dates.append(date)
        dates.sort()

        header = ["Date"]
        header.extend(precincts)

        writer = csv.writer(csvfile)
        writer.writerow(header)
        for date in dates:
            row = []
            row.append(date)
            for precinct in precincts:
                if date in date_timeseries[precinct].keys():
                    row.append(date_timeseries[precinct][date])
                else:
                    row.append(0)
            print(row)
            writer.writerow(row)


if __name__ == "__main__":
    path = "/home/dave/Documents/Election Fraud/GreekAngle/Election_Ballot_Applications.csv"
    print_interesting_datapoint(path)