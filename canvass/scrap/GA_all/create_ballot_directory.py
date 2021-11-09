import collections
import csv
import json
from helper_functions import post_updates

def absentee_ballot_generator(absentee_filepath="/home/dave/Documents/Election Fraud/VoterAbsenteeFiles/STATEWIDE.csv"):
    with open(absentee_filepath, errors='replace') as absentee_file:
        generator = csv.DictReader(absentee_file)
        for ballot_application in generator:
            yield ballot_application


def normalize_dict(_dict):
    if type(_dict).__name__ == "defaultdict":
        _dict = dict(_dict)
        for key in _dict.keys():
            _dict[key] = normalize_dict(_dict[key])
    return _dict


def categorize_all_results():
    infinitely_deep_nested_dictionary = lambda: collections.defaultdict(infinitely_deep_nested_dictionary)
    directory_of_absentee_info = infinitely_deep_nested_dictionary()

    absentee_generator = absentee_ballot_generator()
    count = 0
    unicode_errors = 0
    for absentee in absentee_generator:
        count += 1
        post_updates(count, [1, 10, 100, 1000, 10000, 100000])
        county = absentee["County"]
        status = absentee["Ballot Status"]
        reason = absentee["Status Reason"]
        ballot_has_issues = "problems" if len(reason) > 0 else "no problems"
        style = absentee["Ballot Style"]
        precinct = absentee["County Precinct"]

        try:
            directory_of_absentee_info[county][precinct][style]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct][style]["status data"][status] = 1

        try:
            directory_of_absentee_info[county][precinct][style]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct][style]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info[county][precinct][style]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct][style]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info[county][precinct][style]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct][style]["status reason data"]["all status reasons"] = 1

        try:
            directory_of_absentee_info[county][precinct]["all styles"]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct]["all styles"]["status data"][status] = 1

        try:
            directory_of_absentee_info[county][precinct]["all styles"]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct]["all styles"]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info[county][precinct]["all styles"]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct]["all styles"]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info[county][precinct]["all styles"]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info[county][precinct]["all styles"]["status reason data"]["all status reasons"] = 1

        try:
            directory_of_absentee_info[county]["all precincts"][style]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"][style]["status data"][status] = 1

        try:
            directory_of_absentee_info[county]["all precincts"][style]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"][style]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info[county]["all precincts"][style]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"][style]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info[county]["all precincts"][style]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"][style]["status reason data"]["all status reasons"] = 1

        try:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status data"][status] = 1

        try:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info[county]["all precincts"]["all styles"]["status reason data"]["all status reasons"] = 1

        try:
            directory_of_absentee_info["all counties"][style]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info["all counties"][style]["status data"][status] = 1

        try:
            directory_of_absentee_info["all counties"][style]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info["all counties"][style]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info["all counties"][style]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info["all counties"][style]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info["all counties"][style]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info["all counties"][style]["status reason data"]["all status reasons"] = 1

        try:
            directory_of_absentee_info["all counties"]["all styles"]["status data"][status] += 1
        except TypeError:
            directory_of_absentee_info["all counties"]["all styles"]["status data"][status] = 1

        try:
            directory_of_absentee_info["all counties"]["all styles"]["status data"]["all statuses"] += 1
        except TypeError:
            directory_of_absentee_info["all counties"]["all styles"]["status data"]["all statuses"] = 1

        try:
            directory_of_absentee_info["all counties"]["all styles"]["status reason data"][ballot_has_issues] += 1
        except TypeError:
            directory_of_absentee_info["all counties"]["all styles"]["status reason data"][ballot_has_issues] = 1

        try:
            directory_of_absentee_info["all counties"]["all styles"]["status reason data"]["all status reasons"] += 1
        except TypeError:
            directory_of_absentee_info["all counties"]["all styles"]["status reason data"]["all status reasons"] = 1

    return normalize_dict(directory_of_absentee_info)


if __name__ == "__main__":
    filepath = "/home/dave/Documents/Election Fraud/VoterAbsenteeFiles/STATEWIDE.csv"
