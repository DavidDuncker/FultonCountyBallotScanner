import json

default_path = "data/barcodes.json"
#Input: A path to a JSON file containing a "database" of barcodes
    #barcodes["<tabulator>"]["<batch>"]["<ballot>"] = int barcode
#Output: A dictionary associating a batch of ballots with a distribution of barcodes
    #tally_of_barcodes[int <tabulator][int <batch>][int <barcode>] = int <number of occurences of that barcode
def get_tally_of_barcodes(path):
    #Initialize dictionary containing final tally of all barcodes
    tally_of_barcodes = {}

    #Open and load data
    barcode_file = open(path, 'r')
    barcodes = json.loads(barcode_file.read())
    barcode_file.close()

    tally_of_barcodes["total"] = {} #"Total" will contain barcodes as keys and amount as values
    for tabulator in barcodes.keys(): #keys in barcode data are tabulators
        tally_of_barcodes[int(tabulator)] = {} #Gotta make the tabulator and batch keys integers. Cause they are.
        tally_of_barcodes[int(tabulator)]["total"] = {}
        for batch in barcodes[tabulator].keys():
            tally_of_barcodes[int(tabulator)][int(batch)] = {}
            for ballot in barcodes[tabulator][batch].keys():
                #Get ballot barcode; turn it into an int if it's not "software error"
                try:
                    single_barcode = int(barcodes[tabulator][batch][ballot])
                except ValueError:
                    single_barcode = barcodes[tabulator][batch][ballot]
                #Update barcode count on the batch level
                try:
                    tally_of_barcodes[int(tabulator)][int(batch)][single_barcode] += 1
                except KeyError:
                    tally_of_barcodes[int(tabulator)][int(batch)][single_barcode] = 1
                #Update barcode count on the tabulator level
                try:
                    tally_of_barcodes[int(tabulator)]['total'][single_barcode] += 1
                except KeyError:
                    tally_of_barcodes[int(tabulator)]["total"][single_barcode] = 1
                #Update barcode count on the county-wide level:
                try:
                    tally_of_barcodes['total'][single_barcode] += 1
                except KeyError:
                    tally_of_barcodes["total"][single_barcode] = 1
    return tally_of_barcodes


#This function groups batches together if they have a completely equal distribution of barcodes.
#I.e. this is a duplicate batch detector.
def group_together_duplicate_batches(tally_of_barcodes):
    groups_of_identical_batches = []
    for tabulator1 in tally_of_barcodes.keys():
        if tabulator1 != "total":
            for batch1 in tally_of_barcodes[tabulator1].keys():
                if batch1 != "total":
                    group_of_identical_batches = [f"/{tabulator1}/{batch1}"]
                    for tabulator2 in tally_of_barcodes.keys():
                        for batch2 in tally_of_barcodes[tabulator2].keys():
                            if tally_of_barcodes[tabulator1][batch1] == tally_of_barcodes[tabulator2][batch2]\
                                    and (tabulator1 != tabulator2 or batch1 != batch2):
                                group_of_identical_batches.append(f"/{tabulator2}/{batch2}")
                    if len(group_of_identical_batches) > 1:
                        groups_of_identical_batches.append(group_of_identical_batches)
    return groups_of_identical_batches


#This function groups batches together if they have a *similar* distribution of barcodes.
#I.e. this is a duplicate batch detector with some slack for erroneous barcode scans.
def group_together_similar_batches(tally_of_barcodes, min_difference, max_difference):
    groups_of_similar_batches = []
    #Look at each tabulator
    for tabulator1 in tally_of_barcodes.keys():
        if tabulator1 != "total":
            print(f"Working on {tabulator1}...")
            #Look at each batch
            for batch1 in tally_of_barcodes[tabulator1].keys():
                if batch1 != "total":
                    #Prepare to compare this batch to every other batch, and prepare to make a list
                    group_of_similar_batches = [f"/{tabulator1}/{batch1}"]
                    #Look at each tabulator
                    for tabulator2 in tally_of_barcodes.keys():
                        if tabulator2 != "total":
                            #Look at each batch
                            for batch2 in tally_of_barcodes[tabulator2].keys():
                                if batch2 != "total":
                                    #We have to jump through hoops to avoid KeyErrors
                                    # when comparing the keys (i.e. the barcodes) to their values (i.e. the number of each
                                    #barcode)
                                    #Create a list of all barcodes, with duplicates
                                    all_barcodes = list(tally_of_barcodes[tabulator1][batch1].keys())
                                    all_barcodes.extend(list(tally_of_barcodes[tabulator2][batch2].keys()))
                                    # all_barcodes contains duplicates. We need to remove the duplicates
                                    all_unique_barcodes = []
                                    [all_unique_barcodes.append(barcode) for barcode in all_barcodes
                                     if barcode not in all_unique_barcodes]
                                    sum_of_differences = 0
                                    #Now we need to transfer all data from the two batches onto a new dictionary
                                    #with all the barcodes in each dictionary
                                    batch1_barcode_count = {}
                                    batch2_barcode_count = {}
                                    #Transfer data, or initialize a particular barcode count to zero if there's a KeyError
                                    for barcode in all_unique_barcodes:
                                        try:
                                            batch1_barcode_count[barcode] = tally_of_barcodes[tabulator1][batch1][barcode]
                                        except KeyError:
                                            batch1_barcode_count[barcode] = 0
                                        try:
                                            batch2_barcode_count[barcode] = tally_of_barcodes[tabulator2][batch2][barcode]
                                        except KeyError:
                                            batch2_barcode_count[barcode] = 0
                                        #Now add all the differences between the barcodes to sum_of_differences
                                    for barcode in all_unique_barcodes:
                                        difference = abs(batch1_barcode_count[barcode] - batch2_barcode_count[barcode])
                                        sum_of_differences += difference
                                    #Now add the second batch if it's similar enough to the first
                                    if (sum_of_differences >= min_difference) \
                                        and (sum_of_differences <= max_difference) \
                                        and (tabulator1 != tabulator2 or batch1 != batch2):
                                        group_of_similar_batches.append(f"/{tabulator2}/{batch2}")
                    if len(group_of_similar_batches) > 1:
                        groups_of_similar_batches.append(group_of_similar_batches)
    return groups_of_similar_batches


#Input: A path to a JSON file containing a "database" of barcodes
    #barcodes["<tabulator>"]["<batch>"]["<ballot>"] = int barcode
#Output: A dictionary associating a batch of ballots with a distribution of barcodes
    #tally_of_barcodes[int <tabulator][int <batch>][int <barcode>] = int <number of occurences of that barcode
def get_tally_of_ballot_info(path):
    #Initialize dictionary containing final tally of all barcodes
    tally_of_ballot_info = {}

    #Open and load data
    ballot_file = open(path, 'r')
    ballots = json.loads(ballot_file.read())[0]
    ballot_file.close()

    attributes = ["hash", "President", "Senate", "Special Senate"]
    tally_of_ballot_info["total"] = {} #"Total" will contain ballot info as keys and amount as values
    for attribute in attributes:
        tally_of_ballot_info["total"][attribute] = {}

    for tabulator in ballots.keys(): #keys in barcode data are tabulators
        tally_of_ballot_info[int(tabulator)] = {} #Gotta make the tabulator and batch keys integers. Cause they are.
        tally_of_ballot_info[int(tabulator)]["total"] = {}
        for attribute in attributes:
            tally_of_ballot_info[int(tabulator)]["total"][attribute] = {}
        for batch in ballots[tabulator].keys():
            tally_of_ballot_info[int(tabulator)][int(batch)] = {}
            for attribute in attributes:
                tally_of_ballot_info[int(tabulator)][int(batch)][attribute] = {}
            for ballot in ballots[tabulator][batch].keys():
                if ballots[tabulator][batch][ballot] == "software error": #Dealing with errors in ballot reading
                    for attribute in attributes:
                        ballots[tabulator][batch][ballot] = {}
                        ballots[tabulator][batch][ballot][attribute] = "software error"
                    continue
                for attribute in ballots[tabulator][batch][ballot].keys():
                    if attribute not in ["hash", "President", "Senate", "Special Senate"]:
                        continue
                    #Get ballot data
                    value = ballots[tabulator][batch][ballot][attribute]
                    #Update barcode count on the batch level
                    try:
                        tally_of_ballot_info[int(tabulator)][int(batch)][attribute][value] += 1
                    except KeyError:
                        tally_of_ballot_info[int(tabulator)][int(batch)][attribute][value] = 1
                    #Update barcode count on the tabulator level
                    try:
                        tally_of_ballot_info[int(tabulator)]['total'][attribute][value] += 1
                    except KeyError:
                        tally_of_ballot_info[int(tabulator)]['total'][attribute][value] = 1
                    #Update barcode count on the county-wide level:
                    try:
                        tally_of_ballot_info['total'][attribute][value] += 1
                    except KeyError:
                        tally_of_ballot_info["total"][attribute][value] = 1
                    pass
    return tally_of_ballot_info


#This function groups batches together if they have a completely equal distribution of barcodes.
#I.e. this is a duplicate batch detector.
def group_together_duplicate_batches_with_ballot_info(tally_of_ballot_info):
    groups_of_identical_batches = []
    for tabulator1 in tally_of_ballot_info.keys():
        if tabulator1 != "total":
            for batch1 in tally_of_ballot_info[tabulator1].keys():
                if batch1 != "total":
                    group_of_identical_batches = [f"/{tabulator1}/{batch1}"]
                    for tabulator2 in tally_of_ballot_info.keys():
                        for batch2 in tally_of_ballot_info[tabulator2].keys():
                            if tally_of_ballot_info[tabulator1][batch1] == tally_of_ballot_info[tabulator2][batch2]\
                                    and (tabulator1 != tabulator2 or batch1 != batch2):
                                group_of_identical_batches.append(f"/{tabulator2}/{batch2}")
                    if len(group_of_identical_batches) > 1:
                        groups_of_identical_batches.append(group_of_identical_batches)
    return groups_of_identical_batches


#This function groups batches together if they have a *similar* distribution of barcodes.
#I.e. this is a duplicate batch detector with some slack for erroneous barcode scans.
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


if __name__ == "__main__":

    tally_of_ballot_info = get_tally_of_ballot_info("data/ballot_directory_recount.json")
    #tally_of_ballot_info = get_tally_of_ballot_info("data/ballot_directory.json")
    #savefile = open("data/tally_of_ballot_info.json", 'w')
    #savefile.write(json.dumps(tally_of_ballot_info))
    #savefile.close()

    #savefile = open("data/tally_of_ballot_info.json", 'r')
    #tally_of_ballot_info = json.loads(savefile.read())
    #savefile.close()

    similar_batches = group_together_similar_batches_with_ballot_info(tally_of_ballot_info, 0, 40)
    print(similar_batches)

