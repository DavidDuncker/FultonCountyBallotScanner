from helper_functions import post_updates

def isolate_relevant_datasets(description):
    bookmark1 = description.find(" voters not in")
    bookmark2 = description.find("'s list of ")
    dataset1 = description[0:bookmark1]
    dataset2 = description[bookmark1+15:bookmark2]
    return dataset1, dataset2


def get_generator_for_dataset(dataset_name):
    if dataset_name == "Voter History":
        import canvass.voter_history
        return canvass.voter_history.voter_generator()
    elif dataset_name == "Voter Base":
        import canvass.voterbase
        return canvass.voterbase.voterbase_voter_generator()
    elif dataset_name == "EBA Statewide":
        import canvass.eba_statewide
        return canvass.eba_statewide.eba_voter_generator()
    elif dataset_name == "EBA Fulton":
        import canvass.eba_fulton
        return canvass.eba_fulton.eba_voter_generator()
    else:
        raise NameError(f"Dataset name '{dataset_name}' not found")

def get_nonmutual_voters(excluded_voters_database, dataset1, dataset2):
    non_mutual_voters = {}
    for voter_type in excluded_voters_database.keys():
        for datasets in excluded_voters_database[voter_type].keys():
            if dataset1 in datasets and dataset2 in datasets:
                non_mutual_voters[datasets] = excluded_voters_database[voter_type][datasets]

    return non_mutual_voters


def print_patterns(list_of_registrations_of_interest, dataset, column_culling=False):
    data_generator = get_generator_for_dataset(dataset)
    column_partial_names_of_interest = ["election", "status", "style", "ballot", "county", "date"]
    count = 0

    #Turn list into dictionary keys for speed:
    registration_speed_dict = {}
    for voter_registration in list_of_registrations_of_interest:
        registration_speed_dict.update({int(voter_registration): ''})

    for datapoint in data_generator:
        count += 1
        post_updates(count, [1, 10, 100, 1000, 10000, 100000])
        registration_number = -1
        column_names_of_interest = []
        for column_name in datapoint.keys():
            if type(column_name).__name__ == "str" \
                    and "registration" in column_name.lower() \
                    and "date" not in column_name.lower():
                registration_number = int(datapoint[column_name])
                column_names_of_interest.append(column_name)
            for name_fragment in column_partial_names_of_interest:
                if name_fragment in column_name.lower() and column_name not in column_names_of_interest:
                    column_names_of_interest.append(column_name)
        if int(registration_number) in registration_speed_dict.keys():
            if column_culling == True:
                data_print_display = ""
                for column_name in column_names_of_interest:
                    data_print_display += f"{column_name}:\t {datapoint[column_name]}\t"
                data_print_display += "\n"
                print(data_print_display)
            elif column_culling == False:
                print(datapoint)


def missing_voter_data_generator(list_of_registrations_of_interest, dataset):
    data_generator = get_generator_for_dataset(dataset)

    #Turn list into dictionary keys for speed:
    registration_speed_dict = {}
    for voter_registration in list_of_registrations_of_interest:
        registration_speed_dict.update({int(voter_registration): ''})

    for datapoint in data_generator:
        registration_number = -1
        for column_name in datapoint.keys():
            if "registration" in column_name.lower():
                registration_number = datapoint[column_name]
        if int(registration_number) in registration_speed_dict.keys():
            yield datapoint

