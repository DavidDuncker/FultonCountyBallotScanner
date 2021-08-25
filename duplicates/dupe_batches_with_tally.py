
#This function groups batches together if they have a *similar* distribution of hashes.
#I.e. this is a duplicate batch detector with some slack for erroneous scans.
def group_together_similar_batches_with_ballot_info(tally_of_ballot_info, min_difference, max_difference):
    groups_of_similar_batches = []
    #Sort tabulators in numerical order
    tabulators = list(tally_of_ballot_info.keys())
    tabulators = list(map(int, tabulators))
    tabulators.sort()
    tabulators = list(map(str, tabulators))
    #Look at each tabulator
    for tabulator1 in tabulators:
        if tabulator1 != "total":
            print(f"Working on {tabulator1}...")
            #Look at each batch
            for batch1 in tally_of_ballot_info[tabulator1].keys():
                if batch1 != "total":
                    #Prepare to compare this batch to every other batch, and prepare to make a list
                    group_of_similar_batches = [f"/{tabulator1}/{batch1}"]
                    sum_of_differences = 0
                    #Look at each tabulator
                    for tabulator2 in tally_of_ballot_info.keys():
                        if tabulator2 != "total":
                            #Look at each batch
                            for batch2 in tally_of_ballot_info[tabulator2].keys():
                                if batch2 != "total":
                                    #Create a list of hashes
                                    all_hashes = list(tally_of_ballot_info[tabulator1][batch1]['hash'].keys())
                                    all_hashes.extend(list(tally_of_ballot_info[tabulator2][batch2]['hash'].keys()))
                                    #Remove small batches with few ballots from consideration
                                    if len(all_hashes) < 60:
                                        continue
                                    # Remove duplicates from list
                                    all_unique_hashes = []
                                    [all_unique_hashes.append(hash) for hash in all_hashes
                                     if hash not in all_unique_hashes]
                                    sum_of_differences = 0
                                    #Now we need to transfer all data from the two batches onto a new dictionary
                                    #with all the hashes in each dictionary
                                    batch1_hash_count = {}
                                    batch2_hash_count = {}
                                    #Transfer data, or initialize a particular barcode count to zero if there's a KeyError
                                    for hash in all_unique_hashes:
                                        try:
                                            batch1_hash_count[hash] = tally_of_ballot_info[tabulator1][batch1]["hash"][hash]
                                        except KeyError:
                                            batch1_hash_count[hash] = 0
                                        try:
                                            batch2_hash_count[hash] = tally_of_ballot_info[tabulator2][batch2]["hash"][hash]
                                        except KeyError:
                                            batch2_hash_count[hash] = 0
                                        #Now add all the differences between the barcodes to sum_of_differences
                                    for hash in all_unique_hashes:
                                        difference = abs(batch1_hash_count[hash] - batch2_hash_count[hash])
                                        sum_of_differences += difference
                                    #Now add the second batch if it's similar enough to the first
                                    if (sum_of_differences >= min_difference) \
                                        and (sum_of_differences <= max_difference) \
                                        and (tabulator1 != tabulator2 or batch1 != batch2):
                                        group_of_similar_batches.append(f"/{tabulator2}/{batch2} (difference = {sum_of_differences}) ")
                    if len(group_of_similar_batches) > 1:
                        groups_of_similar_batches.append(group_of_similar_batches)
    return groups_of_similar_batches