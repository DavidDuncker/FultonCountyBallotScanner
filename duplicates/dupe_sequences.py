from numba import jit
from numba import cuda
from data import create_ballot_dict
import os


#@cuda.jit()
def create_hash_directory(ballots, sequence_size):
    #Initialize final result
    adjacent_hash_directory = {}

    #Search through each tabulator
    for tabulator in ballots.keys():
        #Initialize tabulator
        adjacent_hash_directory[tabulator] = {}

        #Sort the batch numbers in order
        batches = list(ballots[tabulator].keys())
        batches = list(map(int, batches))
        batches.sort()
        batches = list(map(str, batches))
        for batch in batches:
            adjacent_hash_directory[tabulator][batch] = {}
            ballot_numbers = list(ballots[tabulator][batch].keys())
            ballot_numbers = list(map(int, ballot_numbers))
            ballot_numbers.sort()
            ballot_numbers = list(map(str, ballot_numbers))
            for ballot_index in range(len(ballot_numbers)):
                ballot_number = ballot_numbers[ballot_index]
                #print(f"Ballot index: {ballot_index}; Ballot number: {ballot_number}")
                adjacent_hash_directory[tabulator][batch][ballot_number] = {}
                ballot_hash = ballots[tabulator][batch][ballot_number]['hash']
                adjacent_hash_directory[tabulator][batch][ballot_number]['hash'] = ballot_hash
                adjacent_hash_directory[tabulator][batch][ballot_number]['adjacent_hashes'] = []

                adjacent_hashes = []
                max_distance = int(sequence_size/2)
                for adjacent_ballot_index in range(ballot_index-max_distance, ballot_index+max_distance+1):
                    try:
                        adjacent_ballot_number = ballot_numbers[adjacent_ballot_index]
                    except IndexError:
                        adjacent_hashes = []
                        break
                    #print(f"\tAdjacent ballot number: {adjacent_ballot_number}")
                    adjacent_ballot_hash = ballots[tabulator][batch][adjacent_ballot_number]["hash"]
                    adjacent_hashes.append(adjacent_ballot_hash)
                adjacent_hash_directory[tabulator][batch][ballot_number]['adjacent_hashes'] = adjacent_hashes

    return adjacent_hash_directory


def remove_duplicates_from_list(list):
    # Remove duplicates from list of adjacent hashes
    temp_list = []
    [temp_list.append(x) for x in list if x not in temp_list]
    list = temp_list
    return list


#@cuda.jit()
def find_sequences_of_dupes(adj_hash_dir, maintain_ordering, threshold=0.2):
    total_number_of_ballots = 0
    for tabulator in adj_hash_dir.keys():
        for batch in adj_hash_dir[tabulator].keys():
            for ballot_num in adj_hash_dir[tabulator][batch].keys():
                total_number_of_ballots += 1

    number_of_processed_ballots = 0
    ballot_matches = []
    for tabulator in adj_hash_dir.keys():
        for batch in adj_hash_dir[tabulator].keys():
            for ballot_num in adj_hash_dir[tabulator][batch].keys():
                ballot1 = adj_hash_dir[tabulator][batch][ballot_num]
                sequence_size = len(ballot1['adjacent_hashes'])
                for tabulator2 in adj_hash_dir.keys():
                    for batch2 in adj_hash_dir[tabulator2].keys():
                        for ballot_num2 in adj_hash_dir[tabulator2][batch2].keys():
                            ballot2 = adj_hash_dir[tabulator2][batch2][ballot_num2]
                            if ballot1['hash'] != ballot2['hash']:
                                continue
                            if [tabulator, batch, ballot_num] == [tabulator2, batch2, ballot_num2]:
                                continue
                            if len(ballot1["adjacent_hashes"]) == 0 or len(ballot2["adjacent_hashes"]) == 0:
                                continue
                            ballot_index1 = list(adj_hash_dir[tabulator][batch].keys()).index(ballot_num)
                            ballot_index2 = list(adj_hash_dir[tabulator2][batch2].keys()).index(ballot_num2)
                            if [tabulator, batch] == [tabulator2, batch2] and \
                                    abs(ballot_index2-ballot_index1) < sequence_size:
                                continue

                            number_of_matching_hashes = 0
                            if not maintain_ordering:
                                for hash1 in remove_duplicates_from_list(ballot1["adjacent_hashes"]):
                                    for hash2 in remove_duplicates_from_list(ballot2["adjacent_hashes"]):
                                        if hash1 == hash2:
                                            number_of_matching_hashes += 1
                            if maintain_ordering:
                                number_of_forward_matches = 0
                                number_of_reverse_matches = 0
                                for i in range(len(ballot1["adjacent_hashes"])):
                                    try:
                                        if ballot1["adjacent_hashes"][i] == ballot2["adjacent_hashes"][i]:
                                            number_of_forward_matches += 1
                                    except IndexError:
                                        break
                                for i in range(len(ballot1["adjacent_hashes"])):
                                    try:
                                        if ballot1["adjacent_hashes"][i] == \
                                                ballot2["adjacent_hashes"][len(ballot1["adjacent_hashes"]) - 1 - i]:
                                            number_of_reverse_matches += 1
                                    except IndexError:
                                        break
                                number_of_matching_hashes = max(number_of_forward_matches, number_of_reverse_matches)

                            percent_match = number_of_matching_hashes/len(ballot1["adjacent_hashes"])
                            match1 = f"{tabulator}/{batch}/{ballot_num}"
                            match2 = f"{tabulator2}/{batch2}/{ballot_num2}"
                            if percent_match >= threshold:
                                ballot_matches.append([match1, match2, percent_match])

                number_of_processed_ballots += 1
                if number_of_processed_ballots % 500 == 0:
                    print(f"Number of processed ballots: {number_of_processed_ballots}/{total_number_of_ballots}")

    return ballot_matches


def run(path):
    ballot_directory = create_ballot_dict.create_ballot_dict(path)
    hash_directory = create_hash_directory(ballot_directory, 5)
    matches = find_sequences_of_dupes(hash_directory, True, 0.9)
    return matches


def find_duplicates_in_folder(path):
    dictonary_of_matches = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".csv" in file:
                path_to_ocr = os.path.join(root, file)
                print(f"{path_to_ocr}:")
                matches = run(path_to_ocr)
                print(matches)
                dictonary_of_matches.update({file: matches})

                try:
                    matches = run(path_to_ocr)
                    print(matches)
                    dictonary_of_matches.update({file: matches})
                except:
                    print("Encountered an error. Moving on. \n\n")

    return dictonary_of_matches
