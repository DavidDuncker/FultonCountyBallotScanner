from canvass import eba_statewide, eba_fulton, voter_history, voterbase

def get_lists_of_eba_voters():
    statewide_voter_lists = {}
    statewide_absentee_voter_lists = {}
    statewide_mail_voter_lists = {}
    statewide_inperson_voter_lists = {}
    fulton_voter_lists = {}
    fulton_absentee_voter_lists = {}
    fulton_mail_voter_lists = {}
    fulton_inperson_voter_lists = {}

    print("Searching through Voter History List")
    statewide_voter_dict, statewide_absentee_voter_dict, fulton_voter_dict, \
        fulton_absentee_voter_dict = voter_history.create_dict_of_voters()
    statewide_voter_lists.update({"Voter History": statewide_voter_dict})
    statewide_absentee_voter_lists.update({"Voter History": statewide_absentee_voter_dict})
    fulton_voter_lists.update({"Voter History": fulton_voter_dict})
    fulton_absentee_voter_lists.update({"Voter History": fulton_absentee_voter_dict})

    print("Searching through statewide election ballot applications")
    dict_of_voters, dict_of_mail_voters, dict_of_inperson_voters, dict_of_fulton_voters, \
        dict_of_fulton_mail_voters, dict_of_fulton_inperson_voters = eba_statewide.get_dict_of_voters()
    statewide_absentee_voter_lists.update({"EBA Statewide": dict_of_voters})
    statewide_mail_voter_lists.update({"EBA Statewide": dict_of_mail_voters})
    statewide_inperson_voter_lists.update({"EBA Statewide": dict_of_inperson_voters})
    fulton_absentee_voter_lists.update({"EBA Statewide": dict_of_fulton_voters})
    fulton_mail_voter_lists.update({"EBA Statewide": dict_of_fulton_mail_voters})
    fulton_inperson_voter_lists.update({"EBA Statewide": dict_of_fulton_inperson_voters})

    print("Searching through Fulton County election ballot applications")
    dict_of_voters, dict_of_mail_voters, dict_of_inperson_voters = eba_fulton.get_dict_of_voters()
    fulton_absentee_voter_lists.update({"EBA Fulton": dict_of_voters})
    fulton_mail_voter_lists.update({"EBA Fulton": dict_of_mail_voters})
    fulton_inperson_voter_lists.update({"EBA Fulton": dict_of_inperson_voters})

    print("Searching through statewide Voter Base")
    dict_of_voters, dict_of_fulton_voters = voterbase.get_dict_of_voters()
    statewide_voter_lists.update({"Voter Base": dict_of_voters})
    fulton_voter_lists.update({"Voter Base": dict_of_fulton_voters})

    list_of_voter_lists = {}
    list_of_voter_lists["statewide/all voters"] = statewide_voter_lists
    list_of_voter_lists["statewide/absentee"] = statewide_absentee_voter_lists
    list_of_voter_lists["statewide/mail"] = statewide_mail_voter_lists
    list_of_voter_lists["statewide/in person"] = statewide_inperson_voter_lists
    list_of_voter_lists["fulton/all voters"] = fulton_voter_lists
    list_of_voter_lists["fulton/absentee"] = fulton_absentee_voter_lists
    list_of_voter_lists["fulton/mail"] = fulton_mail_voter_lists
    list_of_voter_lists["fulton/in person"] = fulton_inperson_voter_lists

    return list_of_voter_lists


def print_test_comparisons(list_of_voter_lists):
    for voter_category in list_of_voter_lists.keys():
        print(f"{voter_category}:")
        for data_source in list_of_voter_lists[voter_category].keys():
            print(f"\t{data_source}:\t\t{len(list_of_voter_lists[voter_category][data_source].keys())}")


def get_list_of_excluded_voters(list_of_voter_lists):
    excluded_voters = {}
    for voter_category in list_of_voter_lists.keys():
        list_of_datasets = list(list_of_voter_lists[voter_category].keys())
        if len(list_of_datasets) < 2:
            continue
        excluded_voters[voter_category] = {}
        print(voter_category)
        for dataset1 in list_of_datasets:
            for dataset2 in list_of_datasets:
                if dataset1 == dataset2:
                    continue
                excluded_voter_description = f"{dataset1} voters not in {dataset2}'s list of voters"
                print(f"\t{excluded_voter_description}")
                excluded_voters[voter_category][excluded_voter_description] = []
                for voter_registration_number in list_of_voter_lists[voter_category][dataset1].keys():
                    if voter_registration_number not in list_of_voter_lists[voter_category][dataset2].keys():
                        excluded_voters[voter_category][excluded_voter_description].append(voter_registration_number)

    return excluded_voters


def print_test_of_excluded_voters(excluded_voters):
    for voter_category in excluded_voters.keys():
        print(f"{voter_category}:")
        for data_source in excluded_voters[voter_category].keys():
            print(f"\t{data_source}:\t\t{len(excluded_voters[voter_category][data_source])}")
