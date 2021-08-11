import json
identical_batches = [['/794/25', '/791/32 (difference = 5) '], ['/794/20', '/791/28 (difference = 8) '],
                     ['/794/21', '/791/29 (difference = 13) '], ['/791/19', '/791/26 (difference = 0) '],
                     ['/791/17', '/791/24 (difference = 0) '], ['/791/24', '/791/17 (difference = 0) '],
                     ['/791/26', '/791/19 (difference = 0) '], ['/791/25', '/791/18 (difference = 0) '],
                     ['/791/20', '/791/23 (difference = 8) '], ['/791/29', '/794/21 (difference = 13) '],
                     ['/791/28', '/794/20 (difference = 8) '], ['/791/32', '/794/25 (difference = 5) '],
                     ['/791/23', '/791/20 (difference = 8) '], ['/791/18', '/791/25 (difference = 0) '],
                     ['/816/7', '/816/3 (difference = 22) '], ['/816/5', '/816/6 (difference = 22) '],
                     ['/816/3', '/816/7 (difference = 22) '], ['/816/6', '/816/5 (difference = 22) '],
                     ['/773/24', '/773/22 (difference = 0) '], ['/773/22', '/773/24 (difference = 0) '],
                     ['/802/80', '/802/78 (difference = 0) '], ['/802/78', '/802/80 (difference = 0) '],
                     ['/742/42', '/742/40 (difference = 6) '], ['/742/40', '/742/42 (difference = 6) ']]

ballot_path = "/home/dave/PycharmProjects/FultonCountyBallotScanner/data/ballot_directory_recount.json"
ballot_file = open(ballot_path, 'r')
ballot_data = json.loads(ballot_file.read())[0]
ballot_file.close()
output_string = ""
tally = {"Trump": 0, "Biden": 0, "Other": 0}
for pair in identical_batches:
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
        prez = ""
        if ballot_data[tabulator1][batch1][ballot_number1]["President"] == "Dona":
            tally["Trump"] += 1
            prez = "Trump"
        elif ballot_data[tabulator1][batch1][ballot_number1]["President"] == "Jose":
            tally["Biden"] += 1
            prez = "Biden"
        else:
            tally["Other"] += 1
            prez = "Other"
        print(f"{prez}: Tabulator {tabulator1}, Batch {batch1}, Ballot Number {ballot_number1} matches up with:")
        output_string += f"Tabulator {tabulator1}, Batch {batch1}, Ballot Number {ballot_number1} matches up with:\n"
        if len(matches) == 0:
            print("\t\tNothing")
            output_string += "\t\tNothing\n"
        else:
            for match in matches:
                print(f"\t\tTabulator {tabulator2}, Batch {batch2}, Ballot Number {match}")
                output_string += f"\t\tTabulator {tabulator2}, Batch {batch2}, Ballot Number {match}\n"
    print("\n____________________________________________________\n____________________________________________________\n")
    output_string += "____________________________________________________\n____________________________________________________\n\n"
p="/home/dave/Documents/Election Fraud/recount_dupes.txt"
f=open(p, 'w')
f.write(output_string)
f.close()





ballot_file = open(ballot_json_filepath, 'r')
ballots = json.loads(ballot_file.read())[0]
ballot_file.close()
list_of_ballots = []
ballot_index = 89
first_ballot = {}
first_ballot["tabulator"] = "5162"
first_ballot["batch"] = "120"
first_ballot["ballot"] = str(ballot_index)
first_ballot["filepath"] = helper_functions.get_ballot_path(data_directory, "5162",
                                                            "120", str(ballot_index))
first_ballot["data"] = ballots["5162"]["120"][str(ballot_index)]
second_ballot = {}
second_ballot["tabulator"] = "5162"
second_ballot["batch"] = "147"
second_ballot["ballot"] = str(100 - ballot_index)
second_ballot["filepath"] = helper_functions.get_ballot_path(data_directory, "5162",
                                                             "147", str(100 - ballot_index))
second_ballot["data"] = ballots["5162"]["147"][str(100 - ballot_index)]

list_of_ballots.append(first_ballot)
list_of_ballots.append(second_ballot)

IM = ImageProcessingManager()
list_of_random_images = select_random_images(data_directory, 100)
for random_image in list_of_random_images:
    override_image = 0
    if override_image:
        random_image = override_image
    ballot_image = Image.open(random_image)
    ballot_bitmap = np.asarray(ballot_image)
    cursor = ScanningCursor()
    print("\n\neog " + random_image + "&")
    print(f"\"{random_image}\"")
    locations_of_top_bars, locations_of_side_bars, locations_of_bottom_bars, \
    left_bar_data, right_bar_data = cursor.get_border_bars(ballot_bitmap)

    print(locations_of_top_bars[0][1] - locations_of_top_bars[0][0], locations_of_top_bars[0:2],
          locations_of_top_bars[-1], locations_of_top_bars[-1][1] - locations_of_top_bars[-1][0])
    print(locations_of_side_bars[0][1] - locations_of_side_bars[0][0], locations_of_side_bars[0:2],
          locations_of_side_bars[-1], locations_of_side_bars[-1][1] - locations_of_side_bars[-1][0])
    print(locations_of_bottom_bars[0][1] - locations_of_bottom_bars[0][0], locations_of_bottom_bars[0:2],
          locations_of_bottom_bars[-1], locations_of_bottom_bars[-1][1] - locations_of_bottom_bars[-1][0])
    print(f"Left bar data: {left_bar_data}")
    print(f"Right bar data: {right_bar_data}")



    data_directory, data_has_been_downloaded, browser_type, download_directory = main.load_configuration_information()
    barcodes = scan_all_barcodes(data_directory)
    save_file = open("data/barcodes.json", 'w')
    save_file.write(json.dumps(barcodes))
    save_file.close()
    print(barcodes)

    override_image = 0
    if override_image:
        random_image = override_image
    ballot_image = Image.open(random_image)
    ballot_bitmap = np.asarray(ballot_image)
    ballot_image.close()
    print("\n\neog " + random_image + "&")
    print(f"\"{random_image}\"")
    try:
        serial_number = get_serial_number(ballot_bitmap)
        print(serial_number)
    except:
        print("Error")


    barcode_file = open("data/barcodes.json", 'r')
    barcode_dictionary = json.loads( barcode_file.read() )
    consecutive_barcodes = catalogue_consecutive_barcodes(barcode_dictionary)
    for number in range(2, len(consecutive_barcodes)):
        print(f"{number}: \n {consecutive_barcodes[number]}")
        print("")




    ballot_file = open(ballot_filepath, 'r')
    ballot_data = json.loads(ballot_file.read())[0]
    sortable_ballot_data = {}
    for tabulator in ballot_data.keys():
        sortable_ballot_data[int(tabulator)] = {}
        for batch in ballot_data[tabulator].keys():
            #Just a list, Tabulator, Batch# and date\timestamp (which would have to be a sortable value).
            try:
                date_and_time = ballot_data[tabulator][batch]['1']['date'] + ", " + ballot_data[tabulator][batch]['1']['time']
            except TypeError:
                date_and_time = "Unknown due to software error"
            sortable_ballot_data[int(tabulator)][int(batch)] = date_and_time

    results = ""
    for tabulator in sortable_ballot_data.keys():
        for batch in sortable_ballot_data[tabulator]:
            results += f"{tabulator};{batch};1;{sortable_ballot_data[tabulator][batch]}" + os.linesep
    print(results)
    savefile = open("/home/dave/Desktop/results.txt", 'w')
    savefile.write(results)
    savefile.close()



    groups_of_identical_batches = group_together_duplicate_batches(tally_of_barcodes)
    groups_of_similar_batches = group_together_similar_batches(tally_of_barcodes, 0, 0)
    print(groups_of_identical_batches)
    print(groups_of_similar_batches)

