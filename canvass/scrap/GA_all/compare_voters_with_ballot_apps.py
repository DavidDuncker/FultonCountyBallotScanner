import json


def compare_data(absentee_ballot_directory, voter_directory):
    counties = list(voter_directory.keys())
    counties.sort()
    for county in counties:
        if "all counties" in county:
            abs_bal_dir_data = absentee_ballot_directory[county]["all styles"]['status data']["A"]
        else:
            abs_bal_dir_data = absentee_ballot_directory[county]["all precincts"]["all styles"]['status data']["A"]
        vot_dir_data = voter_directory[county]["absentee"]

        spacing = " " * (20-len(county))
        #print(f"{county}:{spacing}{abs_bal_dir_data}\t\t\t{vot_dir_data}")
        print(f"{county},{abs_bal_dir_data},{vot_dir_data}")


if __name__ == "__main__":
    absentee_ballot_directory_filepath = "/canvass/scrap/GA_all/ballot_directory.json"
    voter_directory_filepath = "/canvass/scrap/GA_all/voter_directory.json"