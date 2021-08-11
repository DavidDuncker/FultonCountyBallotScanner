import OCR_capture
import os
import json
import tally_data_by_batch


def find_corresponding_ballots_in_duplicate_batches(similar_batches, ballot_data):
    output_string = ""
    for pair in similar_batches:
        tabulator1 = pair[0].split('/')[1]
        batch1 = pair[0].split('/')[2]

        tabulator2 = pair[1].split(' ')[0].split("/")[1]
        batch2 = pair[1].split(' ')[0].split("/")[2]

        ballots1 = list(ballot_data[tabulator1][batch1].keys())
        ballots1 = list(map(int, ballots1))
        ballots1.sort()
        ballots1 = list(map(str, ballots1))
        ballots2 = ballot_data[tabulator2][batch2].keys()
        for ballot_number1 in ballots1:
            matches = []
            for ballot_number2 in ballots2:
                hash1 = ballot_data[tabulator1][batch1][ballot_number1]["hash"]
                hash2 = ballot_data[tabulator2][batch2][ballot_number2]["hash"]
                if hash1 == hash2:
                    matches.append(ballot_number2)
            print(f"Tabulator {tabulator1}, Batch {batch1}, Ballot Number {ballot_number1} matches up with:")
            output_string += f"Tabulator {tabulator1}, Batch {batch1}, Ballot Number {ballot_number1} matches up with:\n"
            if len(matches) == 0:
                print("\t\tNothing")
                output_string += "\t\tNothing\n"
            else:
                for match in matches:
                    print(f"\t\tTabulator {tabulator2}, Batch {batch2}, Ballot Number {match}")
                    output_string += f"\t\tTabulator {tabulator2}, Batch {batch2}, Ballot Number {match}\n"
        print(
            "\n____________________________________________________\n____________________________________________________\n")
        output_string += "____________________________________________________\n____________________________________________________\n\n"
    return output_string


if __name__ == "__main__":
    print("To analyze all ballots and look for duplicate batches, you need:\n"
          "1. A directory filled with ballot images\n"
          "2. A directory to load and save the ballot database (database is in JSON format)\n"
          "3. A directory to load and save the list of duplicate batches and ballots\n")
    directory_of_ballot_images = input("Enter the directory containing the ballot images:\n")
    database_directory = input("Enter the directory that currently contains, or will contain, the database:\n")
    similarity_data_directory = input("Enter the directory that will contain data on duplicate batches and ballots\n")
    savefile = os.path.join(database_directory, "ballot_directory_recount_take_1.json")
    ballot_data = {}
    if not os.path.isfile(savefile):
        print("OCR-ing all ballots. This may take several days.")
        ballot_data = OCR_capture.ocr_all_ballots(directory_of_ballot_images, savefile)
    elif os.path.isfile(savefile):
        ballot_database_file = open(savefile, 'r')
        ballot_data = json.loads(ballot_database_file.read())
        ballot_database_file.close()
    print("Tallying up all ballots by batch, and looking for duplicate or near-duplicate batches.")
    tally_of_ballot_info = tally_data_by_batch.get_tally_of_ballot_info(savefile)
    minimum_batch_difference = 0
    maximum_batch_difference = 90
    list_of_similar_batches = tally_data_by_batch.\
        group_together_similar_batches_with_ballot_info(tally_of_ballot_info,
                                                        minimum_batch_difference, maximum_batch_difference)
    print("Similar batches:")
    print(list_of_similar_batches)
    print("Saving info on similar batches and similar ballots...")
    similar_batches_path = os.path.join(similarity_data_directory, "similar_batches.txt")
    similar_batches_file = open(similar_batches_path, 'w')
    similar_batches_file.write(str(list_of_similar_batches))
    similar_batches_file.close()

    print("Saving info on similar ballots")
    text_that_outlines_corresponding_ballots = find_corresponding_ballots_in_duplicate_batches(
                                                        list_of_similar_batches, ballot_data)
    similar_ballots_path = os.path.join(similarity_data_directory, "similar_ballots.txt")
    similar_ballots_file = open(similar_ballots_path, 'w')
    similar_ballots_file.write(text_that_outlines_corresponding_ballots)
    similar_ballots_file.close()
