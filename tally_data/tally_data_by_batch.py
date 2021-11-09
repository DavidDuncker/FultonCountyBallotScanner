import json

from duplicates.dupe_batches_with_tally import group_together_similar_batches_with_ballot_info

default_path = "data/barcodes.json"


#Input: A path to a JSON file containing a "database" of barcodes
    #barcodes["<tabulator>"]["<batch>"]["<ballot>"] = int barcode
#Output: A dictionary associating a batch of ballots with a distribution of barcodes
    #tally_of_barcodes[int <tabulator][int <batch>][int <barcode>] = int <number of occurences of that barcode
def get_tally_of_ballot_info(ballots, attributes):
    #Initialize dictionary containing final tally of all barcodes
    tally_of_ballot_info = {}

    #Open and load data
    #ballot_file = open(path, 'r')
    #ballots = json.loads(ballot_file.read())[0]
    #ballot_file.close()

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
                    if attribute not in attributes:
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


def get_tally_of_ballot_races(ballots, attributes):
    #Initialize dictionary containing final tally of all barcodes
    tally_of_ballot_info = {}

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
                for attribute in ballots[tabulator][batch][ballot]["races"].keys():
                    if attribute not in attributes:
                        continue
                    #Get ballot data
                    value = ballots[tabulator][batch][ballot]["races"][attribute]
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

