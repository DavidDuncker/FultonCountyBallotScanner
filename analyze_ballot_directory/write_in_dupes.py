from collections import Counter

def get_list_of_ballots_with_writeins(ballot_directory):
    #Initialize list of ballots with write-ins:
    write_in_candidates = []
    write_in_dictionary = {}

    #Search through each ballot in the ballot directory:
    for tabulator in ballot_directory.keys():
        for batch in ballot_directory[tabulator].keys():
            for ballot_number in ballot_directory[tabulator][batch].keys():
                ballot = ballot_directory[tabulator][batch][ballot_number]
                for race in ballot['races'].keys():
                    candidate = ballot['races'][race]
                    if "Write-in" in candidate:
                        #Append list of candidates:
                        write_in_candidates.append(candidate)
                        #Append (or create) list of ballots associated with a write-in candidate
                        try:
                            write_in_dictionary[candidate].append(ballot)
                        except KeyError:
                            write_in_dictionary[candidate] = [ballot]

    return write_in_candidates, write_in_dictionary


def get_list_of_identical_writein_ballots(write_in_candidates, write_in_dictionary, max_write_in_frequency):
    #Initialize list of interesting write-in candidates that we'll look at
    interesting_write_ins = []

    #Count the number of times each candidate was written in
    write_in_counter = Counter(write_in_candidates)

    #Get a list of interesting write-in candidates:
    for write_in_candidate in write_in_counter.keys():
        write_in_count = write_in_counter[write_in_candidate]
        if write_in_count > 2 and write_in_count < max_write_in_frequency:
            interesting_write_ins.append(write_in_candidate)

    #Initialize dictionary of write-in candidates associated with numerous ballots with an identical hash:
    write_in_matches = {}

    #Fill in the dictionary of write-in matches:
    for write_in in interesting_write_ins:
        for ballot1 in write_in_dictionary[write_in]:
            tabulator1 = ballot1["Tabulator"]
            batch1 = ballot1["Batch"]
            ballot_num1 = ballot1["Ballot"]
            ballot_address1 = [tabulator1, batch1, ballot_num1]
            hash1 = ballot1['hash']
            for ballot2 in write_in_dictionary[write_in]:
                tabulator2 = ballot2["Tabulator"]
                batch2 = ballot2["Batch"]
                ballot_num2 = ballot2["Ballot"]
                ballot_address2 = [tabulator2, batch2, ballot_num2]
                hash2 = ballot2['hash']
                if ballot_address1 != ballot_address2 and hash1 == hash2:
                    try:
                        write_in_matches[write_in].append([ballot_address1, ballot_address2])
                    except KeyError:
                        write_in_matches[write_in] = []
                        write_in_matches[write_in].append([ballot_address1, ballot_address2])

    return write_in_matches


def print_matches(write_in_matches):
    for i in write_in_matches.keys():
        print(f"{i}:")
        for j in range(len(write_in_matches[i])):
            print(f"\t{write_in_matches[i][j]}")
        print("\n")

