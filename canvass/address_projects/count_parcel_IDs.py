import json
import os


def parse_basic_parcel_data(line):
    sanitized_line = line.replace("'}", '"}').replace("{'", '{"').replace("': '", '": "').replace("', '", '", "').\
        replace("\", '", '", "').replace("\": '", '": "').replace("': \"", '": "').replace("\": \"\"", "\": \"").\
        replace("\"\", \"", "\", \"").replace("\": \"}", "\": \"\"}")
    #print(line)
    #print(sanitized_line)
    #basic_parcel_data = json.loads(line)
    basic_parcel_data = json.loads(sanitized_line)
    return basic_parcel_data


def create_dictionary_of_basic_parcel_data(parcel_data_path="/home/dave/PycharmProjects/FultonCountyBallotScanner/"
                                                            "canvass/address_projects/scrap/"
                                                            "property_webscrape_parcel_basics_all_except_8.txt"):
    parcel_data_file = open(parcel_data_path, 'r')
    dictionary_of_basic_parcel_data = {}
    for line_of_parcel_data in parcel_data_file.readlines():
        parcel_data = parse_basic_parcel_data(line_of_parcel_data)
        parcel_id = parcel_data["Parcel ID"]
        address = parcel_data["Parcel Address"]
        dictionary_of_basic_parcel_data[parcel_id] = address

    parcel_data_file.close()

    return dictionary_of_basic_parcel_data


def update_addresses_on_detailed_parcel(old_datafile="/home/dave/Documents/Election Fraud/canvass/property_data/"
                                                        "Fulton_property_webscrape_v1.0.txt",
                                           new_datafile="/home/dave/Documents/Election Fraud/canvass/property_data/"
                                                        "Fulton_property_webscrape_v1.1.txt"):
    old_file_with_detailed_parcel_data = open(old_datafile, 'r')
    if os.path.exists(new_datafile):
        os.remove(new_datafile)
    new_file_with_detailed_parcel_data = open(new_datafile, 'a')
    dictionary_of_basic_parcel_data = create_dictionary_of_basic_parcel_data()
    number_of_adjusted_addresses = 0
    number_of_unadjusted_addresses = 0
    for old_datafile_line in old_file_with_detailed_parcel_data.readlines():
        parcel_data = json.loads(old_datafile_line)
        #print(parcel_data)
        parcel_id = parcel_data["Parcel ID"]
        parcel_id = parcel_id.replace("  LL", " LL")
        try:
            new_parcel_address = dictionary_of_basic_parcel_data[parcel_id]
            number_of_adjusted_addresses += 1
        except KeyError:
            #print(parcel_id)
            try:
                new_parcel_address = parcel_data["Property Location"]
            except KeyError:
                new_parcel_address = ""
            number_of_unadjusted_addresses += 1
        parcel_data["Property Location"] = new_parcel_address
        new_file_with_detailed_parcel_data.write(json.dumps(parcel_data) + "\n")
    print(f"Number of adjusted addresses: {number_of_adjusted_addresses}")
    print(f"Number of unadjusted addresses: {number_of_unadjusted_addresses}")
    print(f"\nNew file: {new_datafile}")

    return True





if __name__ == "__main__":
    path_to_parcel_data = "property_webscrape_parcel_basics.txt"
    parcel_data_file = open(path_to_parcel_data)
    dictionary_with_parcel_IDs_as_keys = {} #Dictionaries are efficient at sorting through keys, and keep the keys unique
    for line in parcel_data_file.readlines():
        #For the record:
        #Turning a string into a python dictionary is a difficult task.
        #
        #JSON makes it easy, but we screwed up the way we wrote the dictionary into the file, so we need to convert
        #the single quotes into double quotes
        #
        #What makes this more complicated is that some parcels have owners that contain a single quote (i.e. apostrophe)
        #in their name, which caused our software to automatically turn all the single quotes surrounding the name
        #into double quotes, which led to some weird, cascading failures.
        #
        #I could go on, but to really understand all the craziness that went on behind the scenes,
        #just modify the following line:
        sanitized_line = line.replace("{'", '{"').replace("': '", '": "').replace("', '", '", "').replace("'}", '"}').replace(
            "\", '", '", "').replace("\": '", '": "').replace("': \"", '": "')
        try:
            parcel_id = json.loads(sanitized_line)["Parcel ID"]
        except:
            print("Error in parsing the JSON data. Let's play a game. Find the differences between the following 2 lines:")
            print(line)
            print(sanitized_line)
            print("\n\n")
        dictionary_with_parcel_IDs_as_keys.update({parcel_id: None})
    print(f"The number of unique parcel IDs: {len(dictionary_with_parcel_IDs_as_keys.keys())}")


