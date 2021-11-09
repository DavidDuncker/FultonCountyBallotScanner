from canvass import voter_history
import csv

def get_voter_history_dict(voter_history_filepath):
    voter_history_file = open(voter_history_filepath, 'r')
    voters = {}
    line_count = 0
    for line in voter_history_file.readlines():
        line_count += 1
        #post_updates(line_count, [1, 10, 100, 1000, 10000, 100000, 1000000])
        voter = voter_history.analyze_voter_history_line(line)
        if voter['election date'] != '20201103' or voter['county'] != 'FULTON' or voter['election type'] != '003':
            continue
        if voter['absentee'] != "Y":
            continue
        try:
            voters[ voter['reg number'] ].append(voter)
        except KeyError:
            voters[voter['reg number']] = [voter]
    return voters

def get_absentee_dict(eba_filepath):
    voters = {}
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
            if len(row['Status Reason']) == 0:
                continue
            if row["Ballot Style"] != "MAILED":
                continue
            registration_number = row['Voter Registration']
            try:
                voters[registration_number].append(row)
            except KeyError:
                voters[registration_number] = [row]

    return voters

if __name__ == "__main__":
    eba_filepath = "/home/dave/Documents/Election Fraud/GreekAngle/Election_Ballot_Applications.csv"
    voter_history_filepath = "/home/dave/Documents/Election Fraud/35209.TXT"