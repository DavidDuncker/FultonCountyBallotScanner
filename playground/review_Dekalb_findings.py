from data import create_ballot_dict

dekalb_mc1_text_filepath = "/home/dave/Documents/Election Fraud/text_files/DeKalb.txt"
dekalb_mc2_text_filepath = "/home/dave/Documents/Election Fraud/text_files/DeKalb_MC2.txt"
dekalb_mc1_csv_filepath = "/home/dave/Documents/Election Fraud/Ballot images/DeKalb MC1 Ballots v3.csv"
dekalb_mc2_csv_filepath = "/home/dave/Documents/Election Fraud/Ballot images/DeKalb MC2 Ballots v3.csv"


def parse_MadLs_textfile_into_list_of_pairs_of_filenames(file_path):
    expected_number_of_matches = 0
    list_of_matches = []

    text_file_with_information = open(file_path, 'r')
    full_text = text_file_with_information.read()
    list_of_matching_batches = full_text.split("Batch ")[1:]
    match_index = 0
    count = 0
    for matching_batches in list_of_matching_batches:
        count += 1
        print(count)
        dictionary_of_match_data = {}

        lines_of_data = matching_batches.split("\n")
        first_line_of_data = lines_of_data[0].split()
        tabulator_1 = first_line_of_data[0].split("_")[0]
        tabulator_1 = str(int(tabulator_1))
        tabulator_1 = "0" * (5 - len(tabulator_1)) + tabulator_1

        batch_1 = first_line_of_data[0].split("_")[1]
        batch_1 = str(int(batch_1))
        batch_1 = "0" * (5 - len(batch_1)) + batch_1

        tabulator_2 = first_line_of_data[3].split("_")[0]
        tabulator_2 = str(int(tabulator_2))
        tabulator_2 = "0" * (5 - len(tabulator_2)) + tabulator_2

        batch_2 = first_line_of_data[3].split("_")[1]
        batch_2 = str(int(batch_2))
        batch_2 = "0" * (5 - len(tabulator_1)) + batch_2

        number_of_matches = int(first_line_of_data[5])
        expected_number_of_matches += number_of_matches

        for line_index in range(1, len(lines_of_data)-1):
            line_of_data = lines_of_data[line_index].split()
            batch_1_start = line_of_data[0].split("->")[0]
            batch_1_start = int(batch_1_start)
            batch_1_end = line_of_data[0].split("->")[1]
            batch_1_end = int(batch_1_end)

            batch_2_start = line_of_data[2].split("->")[0]
            batch_2_start = int(batch_2_start)
            batch_2_end = line_of_data[2].split("->")[1]
            batch_2_end = int(batch_2_end)

            if line_of_data[1] == "matches":
                direction_index = 1
            elif line_of_data[1] == "reversed":
                direction_index = -1

            list_of_batch_1_ballots = [x for x in range(batch_1_start, batch_1_end + 1, 1)]
            list_of_batch_2_ballots = [x for x in range(batch_2_start, batch_2_end + direction_index, direction_index)]

            for i in range(0, len(list_of_batch_1_ballots)):
                ballot_1 = list_of_batch_1_ballots[i]
                ballot_1 = "0" * (6 - len(str(ballot_1))) + str(ballot_1)

                ballot_2 = list_of_batch_2_ballots[i]
                ballot_2 = "0" * (6 - len(str(ballot_2))) + str(ballot_2)

                filename_1 = f"{tabulator_1}_{batch_1}_{ballot_1}"
                filename_2 = f"{tabulator_2}_{batch_2}_{ballot_2}"

                list_of_matches.append([filename_1, filename_2])

    return list_of_matches, expected_number_of_matches


def get_list_of_unique_filenames(list_of_matches):
    dict_of_filenames = {}
    for match in list_of_matches:
        dict_of_filenames.update({match[0]: None})
        dict_of_filenames.update({match[1]: None})

    list_of_unique_filenames = list(dict_of_filenames.keys())
    return list_of_unique_filenames


def analyze_duplicate_ballot_directory(list_of_matches, ballot_directory):
    presidential_tally = {}
    senate1_tally = {}
    senate2_tally = {}

    presidential_tally_for_unique_hashes = {}
    senate1_tally_for_unique_hashes = {}
    senate2_tally_for_unique_hashes = {}

    dict_of_unique_hashes = {}
    for match in list_of_matches:
        [tabulator_1, batch_1, ballot_1] = match[0].split("_")
        tabulator_1 = str(int(tabulator_1))
        batch_1 = str(int(batch_1))
        ballot_1 = str(int(ballot_1))

        [tabulator_2, batch_2, ballot_2] = match[1].split("_")
        tabulator_2 = str(int(tabulator_2))
        batch_2 = str(int(batch_2))
        ballot_2 = str(int(ballot_2))

        print([tabulator_1, batch_1, ballot_1])
        print([tabulator_2, batch_2, ballot_2])

        hash1 = ballot_directory[tabulator_1][batch_1][ballot_1]["hash"]
        hash2 = ballot_directory[tabulator_2][batch_2][ballot_2]["hash"]

        print(hash1)
        print(hash2)
        print("\n\n")
        if hash1 != hash2:
            print("\tWarning! Mismatch!")

        president = ballot_directory[tabulator_1][batch_1][ballot_1]["President"]
        senate1 = ballot_directory[tabulator_1][batch_1][ballot_1]["senate1"]
        senate2 = ballot_directory[tabulator_1][batch_1][ballot_1]["senate2"]
        hash = hash1

        try:
            presidential_tally[president] += 1
        except KeyError:
            presidential_tally[president] = 1

        try:
            senate1_tally[senate1] += 1
        except KeyError:
            senate1_tally[senate1] = 1

        try:
            senate2_tally[senate2] += 1
        except KeyError:
            senate2_tally[senate2] = 1

        if hash not in dict_of_unique_hashes.keys():
            try:
                presidential_tally_for_unique_hashes[president] += 1
            except KeyError:
                presidential_tally_for_unique_hashes[president] = 1

            try:
                senate1_tally_for_unique_hashes[senate1] += 1
            except KeyError:
                senate1_tally_for_unique_hashes[senate1] = 1

            try:
                senate2_tally_for_unique_hashes[senate2] += 1
            except KeyError:
                senate2_tally_for_unique_hashes[senate2] = 1

        dict_of_unique_hashes.update({hash: None})

    return presidential_tally, senate1_tally, senate2_tally, presidential_tally_for_unique_hashes,
    senate1_tally_for_unique_hashes, senate2_tally_for_unique_hashes, list(dict_of_unique_hashes.keys())



def run(path_to_MadL_textfile, path_to_parsed_ballot_image_data):
    list_of_matches, expected_number_of_matches = parse_MadLs_textfile_into_list_of_pairs_of_filenames(path_to_MadL_textfile)
    list_of_unique_filenames = get_list_of_unique_filenames(list_of_matches)

    ballot_directory = create_ballot_dict.create_ballot_dict(path_to_parsed_ballot_image_data)

    presidential_tally, senate1_tally, senate2_tally, presidential_tally_for_unique_hashes, \
    senate1_tally_for_unique_hashes, senate2_tally_for_unique_hashes, list_of_unique_hashes \
        = analyze_duplicate_ballot_directory(list_of_matches, ballot_directory)

    print(f"Number of matches: {len(list_of_matches)}")
    print(f"Number of ballots that have at least one doppleganger: {len(list_of_unique_filenames)}")
    print(f"Number of unique hashes within list of duplicates: {len(list_of_unique_hashes)}")
    print(f"Presidential tally: {presidential_tally}")
    print(f"Senate 1 tally: {senate1_tally}")
    print(f"Senate 2 tally: {senate2_tally}")
    print(f"Presidential tally, if every unique ballot signature counted only once: {presidential_tally_for_unique_hashes}")
    print(f"Senate 1 tally, if every unique ballot signature counted only once: {senate1_tally_for_unique_hashes}")
    print(f"Senate 2 tally, if every unique ballot signature counted only once: {senate2_tally_for_unique_hashes}")

