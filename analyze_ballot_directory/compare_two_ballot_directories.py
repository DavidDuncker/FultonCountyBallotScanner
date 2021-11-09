#The purpose of this is to find ballots that are in 1 ballot directory but are not in another ballot directory


def turn_ballot_directory_into_dictionary_of_ballot_signatures(ballot_directory, tabulators = "All"):
    dictionary_of_ballot_signatures = {}

    allowable_tabulators = []
    if type(tabulators).__name__ != "list":
        allowable_tabulators = ballot_directory.keys()
    else:
        allowable_tabulators = tabulators

    for tabulator in ballot_directory.keys():
        if tabulator not in allowable_tabulators:
            continue
        for batch in ballot_directory[tabulator].keys():
            for ballot_number in ballot_directory[tabulator][batch].keys():
                ballot_data = ballot_directory[tabulator][batch][ballot_number]
                filename = ""
                signature = ""
                for data_label in ballot_data.keys():
                    if "file" in data_label.lower() and "name" in data_label.lower():
                        filename = ballot_data[data_label]
                    if "hash" in data_label.lower() or "signature" in data_label.lower():
                        signature = ballot_data[data_label]

                try:
                    dictionary_of_ballot_signatures[signature].append(filename)
                except KeyError:
                    dictionary_of_ballot_signatures[signature] = [filename]

    return dictionary_of_ballot_signatures


def compare_two_sets_of_ballot_signatures(first_set_of_ballots, second_set_of_ballots):
    ballots_in_first_set_but_not_second_set = []
    for signature in first_set_of_ballots.keys():
        if signature not in second_set_of_ballots.keys():
            ballots_in_first_set_but_not_second_set