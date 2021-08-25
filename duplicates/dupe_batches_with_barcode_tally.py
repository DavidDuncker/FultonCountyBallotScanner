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