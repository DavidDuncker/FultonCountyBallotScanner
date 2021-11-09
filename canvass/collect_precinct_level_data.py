from canvass import eba_statewide
from canvass import voter_history
from canvass import voterbase
from helper_functions import post_updates
from collections import defaultdict


def collect_absentee_ballot_data(absentee_generator=eba_statewide.eba_voter_generator()):
    dict_of_ballot_applications_by_registration_number = {}
    count = 0
    for absentee_ballot_application in absentee_generator:
        county = absentee_ballot_application["County"]
        registration_number = absentee_ballot_application["Voter Registration #"]
        registration_number = str(int(registration_number))
        precinct = absentee_ballot_application["County Precinct"]
        vote_status_2020 = False
        dict_of_ballot_applications_by_registration_number[registration_number] = [county, precinct, vote_status_2020]

        count += 1
        post_updates(count, [100, 1000, 10000, 100000])

    return dict_of_ballot_applications_by_registration_number


def append_data_with_vote_status(dict_of_ballot_applications, voter_history_generator=voter_history.voter_generator()):
    count = 0
    for voter in voter_history_generator:
        county = voter["county"]
        registration_number = voter["registration number"]
        registration_number = str(int(registration_number))
        absentee_status = "absentee" if voter["absentee"] == "Y" else "election day"
        if dict_of_ballot_applications[registration_number][0] != county:
            print(f"County does not match!!!!\n{voter}")
        dict_of_ballot_applications[registration_number][2] = absentee_status

        count += 1
        post_updates(count, [100, 1000, 10000, 100000])


    return dict_of_ballot_applications


def collect_voter_history_data(voter_generator=voter_history.voter_generator()):
    print("Collecting voter history data")
    count = 0
    dict_of_voters = {}
    for voter in voter_generator:
        county = voter["county"]
        registration_number = voter["registration number"]
        registration_number = str(int(registration_number))
        early_status = True if voter["absentee"] == "Y" else False
        dict_of_voters[registration_number] = {"county": county, "voted_early": early_status}

        count += 1
        post_updates(count, [1000, 10000, 100000, 500000, 1000000])

    return dict_of_voters


def append_data_with_voterbase_data(dict_of_voters, voter_generator=voterbase.voterbase_voter_generator()):
    print("Appending with voterbase data")
    count = 0
    number_of_contradictory_counties = 0
    number_of_ghost_voters = 0
    for voter in voter_generator:
        count += 1
        post_updates(count, [100, 1000, 10000, 100000, 500000, 1000000])

        county = voter["COUNTY_NAME"]
        registration_number = voter["REGISTRATION_NUMBER"]
        registration_number = str(int(registration_number))
        precinct = voter["COUNTY_PRECINCT_ID"]
        try:
            dict_of_voters[registration_number]
        except KeyError:
            continue
        if county.upper() != dict_of_voters[registration_number]["county"].upper():
            #print("Contradicting counties!")
            #print(voter)
            #print(dict_of_voters[registration_number]["county"])
            precinct = "UNKNOWN, 2 CONTRADICTORY COUNTIES OF RESIDENCE ACCORDING TO 2 DATASETS"
            number_of_contradictory_counties += 1

        dict_of_voters[registration_number]["precinct"] = precinct

    print(f"Number of contradictory counties between the 2 datasets: {number_of_contradictory_counties}")

    count = 0
    for registration_number in dict_of_voters.keys():
        count += 1
        post_updates(count, [100000, 500000, 1000000, 2000000])
        try:
            dict_of_voters[registration_number]["precinct"]
        except KeyError:
            number_of_ghost_voters += 1
            dict_of_voters[registration_number]["precinct"] = "UNKNOWN, NO REGISTRATION DATA AVAILABLE"

        count += 1
        post_updates(count, [1000, 10000, 100000, 500000, 1000000])

    print(f"Number of ghost voters with no registration info: {number_of_ghost_voters}")

    return dict_of_voters


def tally_canvass_data_by_county_and_precinct(dict_of_voters):
    infinitely_nested_dictionary_class = lambda: defaultdict(infinitely_nested_dictionary_class)
    canvass_data = infinitely_nested_dictionary_class()

    for registration_number in dict_of_voters.keys():
        county = dict_of_voters[registration_number]["county"]
        voted_early = dict_of_voters[registration_number]["voted_early"]
        absentee_status = "Early Voters" if voted_early else "Election Day Voters"
        precinct = dict_of_voters[registration_number]["precinct"]

        try:
            canvass_data[county][precinct]["All Voters"] += 1
        except TypeError:
            canvass_data[county][precinct]["All Voters"] = 1

        try:
            canvass_data[county][precinct][absentee_status] += 1
        except TypeError:
            canvass_data[county][precinct][absentee_status] = 1

    def recursively_de_infinitize_dictionary(inf_dict):
        if type(inf_dict).__name__ == "defaultdict":
            de_infinitized_dict = dict(inf_dict)
            for key in inf_dict.keys():
                de_infinitized_dict[key] = recursively_de_infinitize_dictionary(inf_dict[key])
        else:
            de_infinitized_dict = inf_dict

        return de_infinitized_dict

    canvass_data = recursively_de_infinitize_dictionary(canvass_data)
    return canvass_data


def print_out_results_in_csv_format(tally_of_canvass, delimiter=";"):
    output_string = ""
    output_string += f"County{delimiter}Precinct{delimiter}All Voters{delimiter}Early/Absentee Voters{delimiter}Election Day Voters\n"

    counties = list(tally_of_canvass.keys())
    counties.sort()
    for county in counties:
        precincts = tally_of_canvass[county].keys()
        precincts = list(precincts)
        precincts.sort()

        special_precincts = []
        for precinct in precincts:
            if "UNKNOWN" in precinct:
                special_precincts.append(precinct)

        for precinct in special_precincts:
            if precinct in precincts:
                precincts.remove(precinct)

        formatted_precincts = special_precincts
        formatted_precincts.extend(precincts)

        for precinct in formatted_precincts:
            try:
                all_voters = tally_of_canvass[county][precinct]["All Voters"]
            except KeyError:
                all_voters = 0
            try:
                early_voters = tally_of_canvass[county][precinct]["Early Voters"]
            except KeyError:
                early_voters = 0
            try:
                ed_voters = tally_of_canvass[county][precinct]["Election Day Voters"]
            except KeyError:
                ed_voters = 0

            output_string += f"{county}{delimiter}{precinct}{delimiter}{all_voters}{delimiter}{early_voters}{delimiter}{ed_voters}\n"

    return output_string


def do():
    dict_of_voters = collect_voter_history_data()
    dict_of_voters = append_data_with_voterbase_data(dict_of_voters)
    tally_of_canvass = tally_canvass_data_by_county_and_precinct(dict_of_voters)
    output_string = print_out_results_in_csv_format(tally_of_canvass)

    return tally_of_canvass, output_string

