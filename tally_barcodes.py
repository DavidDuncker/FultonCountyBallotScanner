import json

path = "data/barcodes.json"
#The following function will create what is essentially a histogram of barcodes: it will associate with each tabulator
    #and with each batch a set of barcodes, and the number of each barcode in the batch or tabulator
def get_tally_of_barcodes():
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



if __name__ == "__main__":
    tally_of_barcodes = get_tally_of_barcodes()
    groups_of_similar_batches = group_together_similar_batches(tally_of_barcodes, 5, 0)
    print(groups_of_similar_batches)
    #Write results into JSON files
#    barcode_tally_file = open("data/barcode_tally.json", 'w')
#    barcode_tally_file.write(json.dumps(tally_of_barcodes))
#    barcode_tally_file.close()

#    duplicate_batches_file = open("data/batches_with_duplicate_barcodes.json", "w")
#    duplicate_batches_file.write(json.dumps((groups_of_identical_batches)))
#    duplicate_batches_file.close()

