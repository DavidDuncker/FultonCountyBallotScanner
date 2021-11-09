import collections

from canvass import voter_history
from helper_functions import post_updates


def voter_generator(voter_history_filepath="/home/dave/Documents/Election Fraud/35209.TXT"):
    voter_history_file = open(voter_history_filepath, 'r')
    for line in voter_history_file.readlines():
        voter = voter_history.analyze_voter_history_line(line)
        yield voter


def normalize_dict(_dict):
    if type(_dict).__name__ == "defaultdict":
        _dict = dict(_dict)
        for key in _dict.keys():
            _dict[key] = normalize_dict(_dict[key])
    return _dict


def categorize_all_results():
    infinitely_deep_nested_dictionary = lambda: collections.defaultdict(infinitely_deep_nested_dictionary)
    directory_of_voter_info = infinitely_deep_nested_dictionary()

    voter__generator = voter_generator()
    count = 0
    for voter in voter__generator:
        count += 1
        post_updates(count, [1, 10, 100, 1000, 10000, 100000])
        election_date = voter["election date"]
        election_type = voter['election type']
        if election_date != '20201103' or election_type != '003':
            continue
        county = voter["county"]
        absentee_status = "absentee" if voter["absentee"] == "Y" else "non-absentee"

        try:
            directory_of_voter_info[county][absentee_status] += 1
        except TypeError:
            directory_of_voter_info[county][absentee_status] = 1

        try:
            directory_of_voter_info[county]["all voters"] += 1
        except TypeError:
            directory_of_voter_info[county]["all voters"] = 1

        try:
            directory_of_voter_info["all counties"][absentee_status] += 1
        except TypeError:
            directory_of_voter_info["all counties"][absentee_status] = 1

        try:
            directory_of_voter_info["all counties"]["all voters"] += 1
        except TypeError:
            directory_of_voter_info["all counties"]["all voters"] = 1

    return normalize_dict(directory_of_voter_info)



if __name__ == "__main__":
    voter_history_csv = "/home/dave/Documents/Election Fraud/35209.TXT"

