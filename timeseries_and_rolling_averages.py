import json
from random import randint
from datetime import datetime, timedelta


#Input: A path to a file containing a JSON "ballot file".
    #ballot_file[1] includes all the errors
    #ballot_file[0] contains a dictionary
    #ballot_file[0][<int tabulator>][<int batch>][<ballot>]
#       = {filename: "", time: "", date: "", scanned_on: "", Tabulator: "", Batch: "", Poll ID: "", Ballot ID: "",
#       hash: "", President: "", Senate: "", Special Senate: "", PSC1: "", PSC2: "", Race6: "", .... Race14: ""}
#
#Output:
    #A dictionary: ordered_series[<Tabulator>][<Integer>] = The <Integer>th ballot scanned by <Tabulator>
def create_ordered_timeseries_of_ballots(ballot_filepath):
    #Open up the dictionary of ballots
    ballot_file = open(ballot_filepath, 'r')
    ballots = json.loads(ballot_file.read())[0]
    #Start creating a timeseries filled with timestamped ballots from each tabulator
    #time_series[<Tabulator>][<Sortable DateTime>] = <ballot data> is what I'm going for
    time_series = {}
    time_series["All"] = {}
    for tabulator in ballots.keys():
        time_series[int(tabulator)] = {}
        for batch in ballots[tabulator].keys():
            for ballot in ballots[tabulator][batch].keys():
                try:
                    date = ballots[tabulator][batch][ballot]['date']
                    time = ballots[tabulator][batch][ballot]['time']
                except TypeError:  # Sometimes "ballots[tabulator][batch][ballot]" equals "software error"
                    date = "software error"
                    time = "software error"
                datetime = f"{date} {time}.{randint(0, 9999)}"
                time_series[int(tabulator)][datetime] = ballots[tabulator][batch][ballot]
                time_series["All"][datetime] = ballots[tabulator][batch][ballot]
    #Start creating a chronologically ordered list of each ballot run through the tabulator
    #ordered_series[<Tabulator>][<Integer>] = <ballot data> is what I'm going for
    ordered_series = {}
    for tabulator in time_series.keys():
        ordered_series[tabulator] = {}
        #Get all datetimes
        list_of_datetimes = time_series[tabulator].keys()
        #Convert to list to allow sorting
        list_of_datetimes = list(list_of_datetimes)
        #Sort
        list_of_datetimes.sort()
        for i in range(0, len(list_of_datetimes)):
            datetime = list_of_datetimes[i]
            ordered_series[tabulator][i] = time_series[tabulator][datetime]
    return ordered_series


#Goal:
#Input: an "ordered series"
#Output: A dictionary of time-ordered lists of a rolling average, suitable for graphing with PyPlot
#Example:
#rolling_average[<tabulator>][attribute] =  [attribute1, attribute2, ...]
#Do NOT calculate the
def determine_rolling_average(ordered_series, number_of_ballots_counted, savefile_path):
    ballot_processing_count = 0
    #Initialize Rolling Average variable
    rolling_average = {}
    #Look at the data from each tabulator, one tabulator at a time
    for tabulator in ordered_series.keys():
        rolling_average[tabulator] = {}
        #Initialize the list of averages for Biden, Trump, Ossoff, and Warnock, associated with the Tabulator
        biden_vote_rolling_average = []
        trump_vote_rolling_average = []
        adjudication_rolling_average = []
        #ossoff_vote_rolling_average = []
        #warnock_vote_rolling_average = []
        #Initialize the list of percentages of duplicate hashes, associated with the Tabulator
        percentage_of_unique_ballots_rolling_average = []
        #Initialize the list of timestamps
        list_of_timestamps = []


        #When you take a rolling average of 30 ballots, then the previous 29 ballots
        #will have no rolling average associated with them
        #So we need to fill the first N-1 entries of the rolling averages with 0
        #That way, the ballots in the list of rolling averages
        #will line up with the ballots in the ordered series
        for entry in range(0, number_of_ballots_counted-1):
            biden_vote_rolling_average.append(0)
            trump_vote_rolling_average.append(0)
            #ossoff_vote_rolling_average.append(0)
            #warnock_vote_rolling_average.append(0)
            adjudication_rolling_average.append(0)
            percentage_of_unique_ballots_rolling_average.append(0)
            list_of_timestamps.append(0)

        #If we're doing a rolling average of the previous 30 ballots, then we'll start on
            #the 29th ballot, calculate the average of ballots 0-29, and make that average
            #be the first average in the list of ballots
            #Same logic applies to a rolling average of N ballots
        for current_ballot in range(number_of_ballots_counted-1, len(ordered_series[tabulator].keys())):
            #Initialize the lists that we will be taking the averages of
            list_of_presidential_picks = []
            #list_of_senate_picks = []
            #list_of_special_senate_picks = []
            #Initialize the list of N previous ballot hashes; we need a special operation for them
            list_of_adjudications = []
            list_of_ballot_hashes = []
            #Initialize the list of timestamps. We need an X axis.

            #If we're taking a rolling average of 30 ballots, then the rolling average that is associated with
                #the 29th ballot will be the average of ballots 0 through 29
                #So we're essentially scanning the previous N ballots before the current ballot
                #and then adding them to a list of scanned back-data for processing
            for previous_ballot in range(current_ballot - number_of_ballots_counted + 1, current_ballot):
                #Add the presidential pick to the list of scanned back-data
                list_of_presidential_picks.append(
                    ordered_series[tabulator][previous_ballot]["President"])
                #Add the Senate pick to the list of scanned back-data
                #list_of_senate_picks.append(
                #    ordered_series[tabulator][previous_ballot]["Senate"])
                #Add the Special Senate Election pick to the list of scanned back-data
                #list_of_special_senate_picks.append(
                #    ordered_series[tabulator][previous_ballot]["Special Senate"])
                #Add a list of ballot adjudications
                if ordered_series[tabulator][previous_ballot]["Adjudicated"]:
                    list_of_adjudications.append(ordered_series[tabulator][previous_ballot]["Adjudicated"])
                #Add the ballot hash to the list of scanned back-data
                list_of_ballot_hashes.append(
                    ordered_series[tabulator][previous_ballot]["hash"])

            #Count the number of scanned Biden selections, divide by number of ballots counted
            biden_average = list_of_presidential_picks.count("Jose")/number_of_ballots_counted
            biden_average = round(biden_average*100, 2)
            #Append the result to the list of rolling averages
            biden_vote_rolling_average.append(biden_average)

            #Count the number of scanned Trump selections, divide by number of ballots counted
            trump_average = list_of_presidential_picks.count("Dona")/number_of_ballots_counted
            trump_average = round(trump_average*100, 2)
            #Append the result to the list of rolling averages
            trump_vote_rolling_average.append(trump_average)

            #Count the number of scanned Ossoff selections, divide by number of ballots counted
            #ossoff_average = list_of_presidential_picks.count("JonO")/number_of_ballots_counted
            #ossoff_average = round(ossoff_average*100, 2)
            #Append the result to the list of rolling averages
            #ossoff_vote_rolling_average.append(ossoff_average)

            #Count the number of scanned Warnock selections, divide by number of ballots counted
            #warnock_average = list_of_presidential_picks.count("Raph")/number_of_ballots_counted
            #warnock_average = round(warnock_average*100, 2)
            #Append the result to the list of rolling averages
            #warnock_vote_rolling_average.append(warnock_average)

            #Count the number of adjudicated ballots
            adjudication_average = list_of_adjudications.count(True)/number_of_ballots_counted
            adjudication_rolling_average.append(adjudication_average)

            #Count the number of duplicate ballot hashes
            #Do this by popping out an element in a list whenever a copy of that element is found.
            number_of_duplicate_hashes = 0
            #Start by going through each hash, one by one
            for hash_index in range(0, len(list_of_ballot_hashes)):
                #Then go through each hash further down the list
                for hash2_index in range(hash_index+1, len(list_of_ballot_hashes)):
                    #If hash 1 and hash 2 are the same, add 1 to the number of apparent duplicates
                    #Then move on to the next ballot
                    if list_of_ballot_hashes[hash_index] == list_of_ballot_hashes[hash2_index]:
                        number_of_duplicate_hashes += 1
                        break

            #Now append the percentage of duplicate ballots:
            percent_duplicates = number_of_duplicate_hashes/len(list_of_ballot_hashes)
            percent_duplicates = round(100*percent_duplicates, 2)
            percentage_of_unique_ballots_rolling_average.append(percent_duplicates)

            #Now append the timestamp
            try:
                list_of_timestamps.append(ordered_series[tabulator][current_ballot]['date'] + " " \
                                      + ordered_series[tabulator][current_ballot]['time'])
            except TypeError: #In case ordered_series[tabulator][current_ballot] equals "software error"
                list_of_timestamps.append("software error")


            ballot_processing_count += 1
            if ballot_processing_count == 10 or ballot_processing_count == 100 or ballot_processing_count == 1000 or \
                ballot_processing_count % 5000 == 0:
                print(f"\tNumber of ballots processed: {ballot_processing_count}")
                savefile = open(savefile_path, 'w')
                savefile.write(json.dumps(rolling_average))
                savefile.close()

            #We still need to add a list of timestamps

        rolling_average[tabulator]['Biden'] = biden_vote_rolling_average
        rolling_average[tabulator]['Trump'] = trump_vote_rolling_average
        #rolling_average[tabulator]['Ossoff'] = ossoff_vote_rolling_average
        #rolling_average[tabulator]['Warnock'] = warnock_vote_rolling_average
        rolling_average[tabulator]['Adjudications'] = adjudication_rolling_average
        rolling_average[tabulator]['Duplicates'] = percentage_of_unique_ballots_rolling_average
        rolling_average[tabulator]['time'] = list_of_timestamps

        if tabulator == 729:
            print(rolling_average[tabulator])
        print(tabulator)

    return rolling_average


#This function will compute Biden's total, or some other metric, before and after a certain point in time
def before_and_after(window_of_time_in_hours, value_of_interest, tabulator, central_point_in_time, ordered_series_path):
    list_of_ballots_before_central_point = []
    list_of_ballots_after_central_point = []
    central_point_in_time = datetime.strptime(central_point_in_time, "%m/%d/%y %H:%M:%S")
    start_of_before_time = central_point_in_time - timedelta(hours=window_of_time_in_hours)
    end_of_after_time = central_point_in_time + timedelta(hours=window_of_time_in_hours)

    ordered_series_file = open(ordered_series_path, 'r')
    ordered_series = json.loads(ordered_series_file.read())
    ordered_series_file.close()

    #Get lists of ballots before and after central point in time
    for ballot_order in ordered_series[tabulator].keys():
        date_time = f"{ordered_series[tabulator][ballot_order]['date']} {ordered_series[tabulator][ballot_order]['time']}"
        date_time = datetime.strptime(date_time, "%m/%d/%y %H:%M:%S")
        if date_time > start_of_before_time and date_time < central_point_in_time:
            list_of_ballots_before_central_point.append(ordered_series[tabulator][ballot_order])
        elif date_time > central_point_in_time and date_time < end_of_after_time:
            list_of_ballots_after_central_point.append(ordered_series[tabulator][ballot_order])

    #Get data from ballots in lists
    before_data = {}
    before_data["All"] = 0
    after_data = {}
    after_data["All"] = 0
    for datapoint in list_of_ballots_before_central_point:
        try:
            before_data[ datapoint[value_of_interest] ] += 1
            before_data["All"] += 1
        except KeyError:
            before_data[datapoint[value_of_interest]] = 1
            before_data["All"] += 1

    for datapoint in list_of_ballots_after_central_point:
        try:
            after_data[ datapoint[value_of_interest] ] += 1
            after_data["All"] += 1
        except KeyError:
            after_data[datapoint[value_of_interest]] = 1
            after_data["All"] += 1

    return before_data, after_data



if __name__ == "__main__":
    ballot_filepath = "data/ballot_directory_backup.json"
    ordered_series = create_ordered_timeseries_of_ballots(ballot_filepath)
    number_of_ballots_in_rolling_average = 200
    threshold_percentage = 30
    rolling_average = determine_rolling_average(ordered_series, number_of_ballots_in_rolling_average,
                                                "data/rolling_average.json")
    print("Starting...")
    for tabulator in ordered_series.keys():
        for i in range(0, len(ordered_series[tabulator])):
            if rolling_average[tabulator]['Duplicates'][i] > threshold_percentage:
                print(f"Percentage of Biden votes: {rolling_average[tabulator]['Biden'][i]}\t\t"
                      f"Rolling average of duplicates: {rolling_average[tabulator]['Duplicates'][i]}\t\t"
                      f"Time: {rolling_average[tabulator]['time'][i]}\t\t"
                      f"Tabulator: {ordered_series[tabulator][i]['Tabulator']}\t\t"
                      f"Batch: {ordered_series[tabulator][i]['Batch']}\t\t"
                      f"Ballot: {ordered_series[tabulator][i]['filename'][-7:-4]}\t\t"
                      f"Hash: {ordered_series[tabulator][i]['hash']}")

