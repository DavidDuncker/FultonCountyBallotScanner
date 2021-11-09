from helper_functions import post_updates
import OCR.OCR_from_sql as _sql
import OCR.transform_ocr_text as _tr
import OCR.manage_ocr_textfiles as _txt

def compare_election_night_to_recount(en_ballots, recount_ballots):
    list_of_missing_ballots = []
    count = 0
    for hash in en_ballots.keys():
        if hash not in recount_ballots.keys():
            for file in en_ballots[hash]:
                count += 1
                #print(f"Hash: {hash}\nFile: {en_ballots[hash]}")
                list_of_missing_ballots.append(f"{file},{hash}")
    print(count)

    return list_of_missing_ballots


def convert_ballot_directory_to_list(en_bd):
    en_ballots = {}
    for t in en_bd.keys():
        for bt in en_bd[t].keys():
            for bl in en_bd[t][bt].keys():
                ballot = en_bd[t][bt][bl]
                try:
                    en_ballots[ballot["hash"]].append(ballot['filename'])
                except KeyError:
                    en_ballots[ballot["hash"]] = [ballot['filename']]
    return en_ballots


def get_recount_hashes():
    recount_ballots = {}
    count = 0
    ballot_generator = _sql.get_a_single_ballot()
    for b in ballot_generator:
        count += 1
        post_updates(count, [100, 1000, 10000])
        ballot_data = _tr.turn_ocr_text_into_hash_with_first_2_letters_of_each_line(b[1])
        ballot_data["filename"] = b[0]
        #recount_ballots[ballot_data["filename"]] = ballot_data["hash"]
        try:
            recount_ballots[ballot_data["hash"]].append(ballot_data["filename"])
        except KeyError:
            recount_ballots[ballot_data["hash"]] = [ballot_data["filename"]]
    return recount_ballots


def load_en_ballots():
    s = "fulton_en_ballots.json"
    d = "/home/dave/Documents/Election Fraud/FultonCountyElectionNight/OCR"
    [en_bd, errors] = _txt.load_all_ocr_texts(d, s)
    return en_bd


def look_for_sequences_of_consecutive_hashes(recount_ballots, minimum_sequence_size):
    sequential_count = 0
    instances_of_a_sequence = []
    previous_hash = ""
    for filename, hash in recount_ballots.items():
        if hash == previous_hash:
            sequential_count += 1
        elif hash != previous_hash:
            if sequential_count >= minimum_sequence_size:
                instances_of_a_sequence.append([filename, sequential_count])
            sequential_count = 0
        previous_hash = hash

    return instances_of_a_sequence


def run_complete_comparison_from_scratch():
    en_ballot_directory = load_en_ballots()
    en_ballot_list = convert_ballot_directory_to_list(en_ballot_directory)
    recount_ballot_list = get_recount_hashes()
    list_of_missing_ballots = compare_election_night_to_recount(en_ballot_list, recount_ballot_list)

    return list_of_missing_ballots


def get_string_to_write_into_csv_file(list_of_missing_ballots):
    csv_string = "File Name, Hash\n"
    for line in list_of_missing_ballots:
        csv_string += line + "\n"
    return csv_string