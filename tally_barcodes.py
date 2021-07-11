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


if __name__ == "__main__":
    tally_of_barcodes = get_tally_of_barcodes()
    groups_of_identical_batches = group_together_duplicate_batches(tally_of_barcodes)
    #Write results into JSON files
    barcode_tally_file = open("data/barcode_tally.json", 'w')
    barcode_tally_file.write(json.dumps(tally_of_barcodes))
    barcode_tally_file.close()

    duplicate_batches_file = open("data/batches_with_duplicate_barcodes.json", "w")
    duplicate_batches_file.write(json.dumps((groups_of_identical_batches)))
    duplicate_batches_file.close()

