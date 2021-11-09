from canvass import eba_statewide, voterbase, voter_history


def get_dict_of_ebas():
    voter_generator = eba_statewide.eba_voter_generator()
    dict_of_registration_numbers = {}
    for voter in voter_generator:
        registration_number = int(voter['Voter Registration #'])
        dict_of_registration_numbers.update({registration_number: None})

    return dict_of_registration_numbers


def get_dict_of_voterbase():
    voter_generator = voterbase.voterbase_voter_generator()
    dict_of_registration_numbers = {}
    for voter in voter_generator:
        registration_number = int(voter['REGISTRATION_NUMBER'])
        dict_of_registration_numbers.update({registration_number: None})

    return dict_of_registration_numbers


def get_dict_of_new_voter_history():
    voter_generator = voter_history.voter_generator()
    dict_of_registration_numbers = {}
    for voter in voter_generator:
        registration_number = int(voter['registration number'])
        dict_of_registration_numbers.update({registration_number: None})

    return dict_of_registration_numbers


def get_dict_of_old_voter_history():
    voter_generator = voter_history.voter_generator(path_to_voter_history_file=
                                                    "/home/dave/Documents/Election Fraud/canvass/Old_Voter_History_File/"
                                                    "35209.TXT")
    dict_of_registration_numbers = {}
    for voter in voter_generator:
        registration_number = int(voter['registration number'])
        dict_of_registration_numbers.update({registration_number: None})

    return dict_of_registration_numbers


def run():
    vh_reg_numbers = get_dict_of_new_voter_history()
    vb_reg_numbers = get_dict_of_voterbase()
    list_of_outcasts = {}
    for voter in vh_reg_numbers.keys():
        if voter not in vb_reg_numbers.keys():
            list_of_outcasts.update({voter: None})

    return list_of_outcasts

