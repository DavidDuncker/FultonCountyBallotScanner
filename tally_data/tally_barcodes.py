import json


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