import json
import os
from collections import defaultdict
from canvass.eba_statewide import eba_voter_generator
from canvass.voter_history import voter_generator as vh_voter_generator
from canvass.voter_history import extensive_voter_generator as vh_extensive_voter_generator
from canvass.voterbase import voterbase_voter_generator as vb_voter_generator
from helper_functions import post_updates


def sanitize_apt_numbers(apt_number):
    apt_number = apt_number.replace("#", "")
    apt_number = apt_number.replace("OFFICE", "")
    apt_number = apt_number.replace("RETAIL", "")
    apt_number = apt_number.replace("RESID", "")
    apt_number = apt_number.replace("UNIT", "")
    apt_number = apt_number.replace("APT", "")
    apt_number = apt_number.replace("ROOM", "")
    apt_number = apt_number.replace("LOT", "")
    apt_number = apt_number.replace("SUITE", "")
    apt_number = apt_number.replace("STE", "")
    apt_number = apt_number.replace(" ", "")
    apt_number = apt_number.replace("", "")
    return apt_number


def sanitize_street_names(street_name):
#    suffix = street_name[-3:]
#    if suffix == " NE" or suffix == " SE" or suffix == " NW" or suffix == " SW":
#        street_name = street_name[:-3]
    street_name = street_name.replace(" XING", " CROSS")
    if street_name[-3:] == " SQ":
        street_name = street_name.replace(" SQ", " SQUARE")
    prefix = street_name[0:2]
    if prefix == "S " or prefix == "N " or prefix == "W " or prefix == "E ":
        prefix = prefix.replace("S ", "SOUTH ")
        prefix = prefix.replace("N ", "NORTH ")
        prefix = prefix.replace("W ", "WEST ")
        prefix = prefix.replace("E ", "EAST ")
        street_name = prefix + street_name[2:]

    street_name = street_name.replace("13TH", "THIRTEENTH")
    street_name = street_name.replace(" PLZ", " PLAZA")
    street_name = street_name.replace(" TRAK", " TRACK")
    street_name = street_name.replace(" SQ ", " SQUARE ")
    street_name = street_name.replace("", "")
    street_name = street_name.replace("", "")

    return street_name


def find_matching_unit(parcel_dictionary, street_number, street_name):
    list_of_units = parcel_dictionary[street_number][street_name].keys()
    for unit in list_of_units:
        if unit == "":
            return unit
        if unit == street_number:
            return unit

    return ""


def match_eba_addresses_to_parcel_dictionary(parcel_dictionary, voter):
    match = False
    street_number = voter["Street #"]
    street_name = sanitize_street_names(voter["Street Name"])
    unit = voter["Apt/Unit"]
    unit = sanitize_apt_numbers(unit)
    city = voter["City"]

    dictionary_of_city_translations = {
        'FAIRBURN': ['SOUTH FULTON', 'CHATTAHOOCHEE HILLS', 'PALMETTO', 'ROSWELL', 'ATLANTA'],
        'ATLANTA': ['SANDY SPRINGS', 'SOUTH FULTON', 'COLLEGE PARK', 'EAST POINT', 'HAPEVILLE'],
        'DULUTH': ['JOHNS CREEK'], 'ALPHARETTA': ['JOHNS CREEK', 'ROSWELL', 'ATLANTA', 'MILTON'],
        'COLLEGE PARK': ['SOUTH FULTON', 'UNION CITY'], 'RIVERDALE': ['SOUTH FULTON'],
        'SUWANEE': ['JOHNS CREEK'], 'DUNWOODY': ['SANDY SPRINGS'],
        'ROSWELL': ['ALPHARETTA', 'JOHNS CREEK', 'ATLANTA', 'SANDY SPRINGS', 'MOUNTAIN PARK'],
        'PALMETTO': ['SOUTH FULTON', 'FAIRBURN', 'CHATTAHOOCHEE HILLS'],
        'CHATTAHOOCHEE ': ['CHATTAHOOCHEE HILLS'],
        'HAPEVILLE': ['ATLANTA', 'SOUTH FULTON'], 'NORCROSS': ['SANDY SPRINGS'],
        'FAYETTEVILLE': ['SOUTH FULTON'], 'JOHNS CREEK': ['ALPHARETTA'],
        'EAST POINT': ['JOHNS CREEK'], 'MILTON': ['ATLANTA', 'ALPHARETTA'],
        'UNION CITY': ['SOUTH FULTON']}

    error_description = ""
    try:
        parcel_dictionary[street_number]
        error_description += f"Street Number {street_number} matches. "
    except KeyError:
        error_description += f"Street Number {street_number} does not match. "
        match = False
        matching_set = []
        return match, matching_set, error_description
    try:
        parcel_dictionary[street_number][street_name]
        error_description += f"Street Name {street_name} matches. "
    except KeyError:
        error_description += f"Street Name {street_name} does not match. "
        match = False
        matching_set = []
        return match, matching_set, error_description
    try:
        parcel_dictionary[street_number][street_name][unit]
        error_description += f"Unit {unit} matches. "
    except KeyError:
        error_description += f"Unit {unit} does not match. "
        alternative_unit = find_matching_unit(parcel_dictionary, street_number, street_name)
        try:
            parcel_dictionary[street_number][street_name][alternative_unit]
            error_description += f"Unit {alternative_unit} matches. "
            unit = alternative_unit
        except KeyError:
            error_description += f"Alternative unit {alternative_unit} does not match. "
            match = False
            matching_set = []
            return match, matching_set, error_description
    try:
        parcel_dictionary[street_number][street_name][unit][city]
        error_description += f"City {city} matches. "
        match = True
        matching_set = [street_number, street_name, unit, city]
        return match, matching_set, error_description
    except KeyError:
        error_description += f"City {city} does not match, \n"
        try:
            dictionary_of_city_translations[city]
        except KeyError:
            error_description += f"City {city} not in directory of replacements. \n" \
                                 f"Possible cities: {parcel_dictionary[street_number][street_name][unit].keys()}"
            match = False
            matching_set = []
            return match, matching_set, error_description
        there_is_a_city_that_matches = False
        for city__ in dictionary_of_city_translations[city]:
                try:
                    parcel_dictionary[street_number][street_name][unit][city__]
                    there_is_a_city_that_matches = True
                    city = city__
                    match = True
                    matching_set = [street_number, street_name, unit, city]
                    return match, matching_set, error_description
                except KeyError:
                    pass
        if there_is_a_city_that_matches:
            error_description += f"City {city} matches"
            match = True
            matching_set = [street_number, street_name, unit, city]
            return match, matching_set, error_description
        else:
            error_description += "No cities match"
            error_description += f" Possible cities: {parcel_dictionary[street_number][street_name][unit].keys()}"
            match = False
            matching_set = []
            return match, matching_set, error_description


def convert_parcel_dictionary_into_parcel_list(parcel_dictionary):
    parcel_list = []
    for street_number in parcel_dictionary.keys():
        for street_name in parcel_dictionary[street_number].keys():
            for unit in parcel_dictionary[street_number][street_name].keys():
                for city in parcel_dictionary[street_number][street_name][unit].keys():
                    parcel_list.append(parcel_dictionary[street_number][street_name][unit][city])

    return parcel_list


def write_parcel_list_to_disk(parcel_list, save_filepath="./parcel_list.txt"):
    save_file = open(save_filepath, 'a')
    for parcel in parcel_list:
        save_file.write(json.dumps(parcel) + "\n")
    save_file.close()


def load_parcel_list_to_memory(save_filepath="./parcel_list.txt", use_as_generator=False):
    parcel_list = []
    save_file = open(save_filepath, 'r')
    for line in save_file.readlines():
        parcel = json.loads(line)
        if use_as_generator:
            yield parcel
        elif use_as_generator == False:
            parcel_list.append(parcel)
    save_file.close()

    if use_as_generator == False:
        return parcel_list


def parcel_data_generator(path_to_parcel_data="/home/dave/Documents/Election Fraud/canvass/property_data/Fulton_property_webscrape_v1.1.txt"):
    with open(path_to_parcel_data) as parcel_data_file:
        for raw_parcel_data in parcel_data_file.readlines():
            #print(raw_parcel_data + "\n")
            parcel_data = json.loads(raw_parcel_data)
            for key, value in parcel_data.items():
                if value == "\xa0":
                    parcel_data[key] = ""
            try:
                parcel_data["Street Number"] = parcel_data["Property Location"].split()[0]
                parcel_data["Street Name"] = ' '.join(parcel_data["Property Location"].split()[1:])
            except IndexError:
                continue
            except KeyError:
                continue
            yield parcel_data


def create_dictionary_of_parcel_data(parcel_data_generator=parcel_data_generator()):
    infinitely_nested_dictionary = lambda: defaultdict(infinitely_nested_dictionary)
    parcel_dictionary = infinitely_nested_dictionary()
    for parcel_data in parcel_data_generator:
        #print(parcel_data)
        #print("\n\n")
        data_container = {}
        data_container["Address Data"] = parcel_data
        data_container["2020 Absentee Ballot Applicants"] = {}
        street_number = parcel_data["Street Number"]
        street_name = parcel_data["Street Name"]
        try:
            unit = parcel_data["Unit"]
            unit = sanitize_apt_numbers(unit)
            city = parcel_data["City"]
        except KeyError:
            continue

        #Test for "Overmatches":
        #if len(str(parcel_dictionary[street_number][street_name][unit][city])) > 20:
            #print(f"Caution: overmatch!\n{street_number} {street_name}, {unit}, {city}")
        parcel_dictionary[street_number][street_name][unit][city] = data_container

    temporary_dictionary = dict(parcel_dictionary)
    for street_number in parcel_dictionary.keys():
        temporary_dictionary[street_number] = dict(parcel_dictionary[street_number])
        for street_name in parcel_dictionary[street_number].keys():
            temporary_dictionary[street_number][street_name] = dict(parcel_dictionary[street_number][street_name])
            for unit in parcel_dictionary[street_number][street_name].keys():
                temporary_dictionary[street_number][street_name][unit] = dict(parcel_dictionary[street_number][street_name][unit])
    parcel_dictionary = temporary_dictionary

    return parcel_dictionary


def test_update_list_of_potential_voters_with_aba_data(parcel_dictionary, statewide_voter_generator=eba_voter_generator()):
    matches = 0
    no_matches = 0
    dictionary_of_city_translations = {
        'FAIRBURN': ['SOUTH FULTON', 'CHATTAHOOCHEE HILLS', 'PALMETTO', 'ROSWELL', 'ATLANTA'],
        'ATLANTA': ['SANDY SPRINGS', 'SOUTH FULTON', 'COLLEGE PARK', 'EAST POINT', 'HAPEVILLE'],
        'DULUTH': ['JOHNS CREEK'], 'ALPHARETTA': ['JOHNS CREEK', 'ROSWELL', 'ATLANTA', 'MILTON'],
        'COLLEGE PARK': ['SOUTH FULTON', 'UNION CITY'], 'RIVERDALE': ['SOUTH FULTON'],
        'SUWANEE': ['JOHNS CREEK'], 'DUNWOODY': ['SANDY SPRINGS'],
        'ROSWELL': ['ALPHARETTA', 'JOHNS CREEK', 'ATLANTA', 'SANDY SPRINGS'],
        'PALMETTO': ['SOUTH FULTON', 'FAIRBURN', 'CHATTAHOOCHEE HILLS'],
        'CHATTAHOOCHEE ': ['CHATTAHOOCHEE HILLS'],
        'HAPEVILLE': ['ATLANTA', 'SOUTH FULTON'], 'NORCROSS': ['SANDY SPRINGS'],
        'FAYETTEVILLE': ['SOUTH FULTON'], 'JOHNS CREEK': ['ALPHARETTA'],
        'EAST POINT': ['JOHNS CREEK'], 'MILTON': ['ATLANTA', 'ALPHARETTA']}
    voters = statewide_voter_generator
    for voter in voters:
        county = voter["County"]
        if county != "FULTON":
            continue
        match, matching_data, error_message = match_eba_addresses_to_parcel_dictionary(parcel_dictionary, voter)

        if match:
            matches += 1
        elif not match:
            no_matches += 1
            print(error_message)
    print(f"\tMatches: {matches}")
    print(f"\tNo Matches: {no_matches}")


def update_list_of_potential_voters_with_aba_data(parcel_dictionary, voters=eba_voter_generator()):
    matches = 0
    no_matches = 0
    dictionary_of_city_translations = {
        'FAIRBURN': ['SOUTH FULTON', 'CHATTAHOOCHEE HILLS', 'PALMETTO', 'ROSWELL', 'ATLANTA'],
        'ATLANTA': ['SANDY SPRINGS', 'SOUTH FULTON', 'COLLEGE PARK', 'EAST POINT', 'HAPEVILLE'],
        'DULUTH': ['JOHNS CREEK'], 'ALPHARETTA': ['JOHNS CREEK', 'ROSWELL', 'ATLANTA', 'MILTON'],
        'COLLEGE PARK': ['SOUTH FULTON', 'UNION CITY'], 'RIVERDALE': ['SOUTH FULTON'],
        'SUWANEE': ['JOHNS CREEK'], 'DUNWOODY': ['SANDY SPRINGS'],
        'ROSWELL': ['ALPHARETTA', 'JOHNS CREEK', 'ATLANTA', 'SANDY SPRINGS'],
        'PALMETTO': ['SOUTH FULTON', 'FAIRBURN', 'CHATTAHOOCHEE HILLS'],
        'CHATTAHOOCHEE ': ['CHATTAHOOCHEE HILLS'],
        'HAPEVILLE': ['ATLANTA', 'SOUTH FULTON'], 'NORCROSS': ['SANDY SPRINGS'],
        'FAYETTEVILLE': ['SOUTH FULTON'], 'JOHNS CREEK': ['ALPHARETTA'],
        'EAST POINT': ['JOHNS CREEK'], 'MILTON': ['ATLANTA', 'ALPHARETTA']}
    for voter in voters:
        county = voter["County"]
        if county != "FULTON":
            continue
        street_number = voter["Street #"]
        street_name = sanitize_street_names(voter["Street Name"])
        unit = voter["Apt/Unit"]
        unit = sanitize_apt_numbers(unit)
        city = voter["City"]
        registration_number = str(int(voter["Voter Registration #"]))
        first_name = voter["First Name"]
        middle_name = voter["Middle Name"]
        last_name = voter["Last Name"]
        ballot_style = voter["Ballot Style"]

        is_a_match, matching_data, error_message = match_eba_addresses_to_parcel_dictionary(parcel_dictionary, voter)
        if not is_a_match:
            no_matches += 1
            continue
        elif is_a_match:
            matches += 1
            [street_number, street_name, unit, city] = matching_data
        try:
            if registration_number not in parcel_dictionary[street_number][street_name][unit][
                city]["2020 Absentee Ballot Applicants"]:
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number] = {}
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number]["First Name"] = first_name
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number]["Middle Name"] = middle_name
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number]["Last Name"] = last_name
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number]["Voted in November 2020"] = False
                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][registration_number]["Ballot Style"] = ballot_style

                residential_address = f"{voter['Street #']} {voter['Street Name']}, {voter['City']}, {voter['State']}"
                mailing_address = f"{voter['Mailing Street #']} {voter['Mailing Street Name']}, {voter['Mailing City']}, {voter['Mailing State']}"

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Residential Address"] = residential_address

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Mailing Address"] = mailing_address

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Ballot Timeline"] = {}

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Ballot Timeline"]['Application Date'] = voter["Application Date"]

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Ballot Timeline"]['Ballot Issued Date'] = voter["Ballot Issued Date"]

                parcel_dictionary[street_number][street_name][unit][city]["2020 Absentee Ballot Applicants"][
                    registration_number]["Ballot Timeline"]['Ballot Return Date'] = voter["Ballot Return Date"]

                matches += 1
        except KeyError:
            no_matches += 1
            continue
    print(f"\tMatches: {matches}")
    print(f"\tNo Matches: {no_matches}")
    return parcel_dictionary


def update_list_of_voters_with_voter_history_data(parcel_generator=load_parcel_list_to_memory(use_as_generator=True),
                                                  voter_generator_2020=vh_voter_generator(),
                                                  voter_generator=vh_extensive_voter_generator()):
    print("\tGetting list of November 2020 voters")
    dict_of_confirmed_voters = {}
    for voter in voter_generator_2020:
        registration_number = str(int(voter["registration number"]))
        dict_of_confirmed_voters.update({registration_number: None})

    print("\tUpdating all voters in all parcels to indicate voting in Nov 2020")
    try:
        os.remove('./parcel_list_temp.txt')
    except FileNotFoundError:
        pass

    count = 0
    bucket_of_modified_parcels = []
    for parcel in parcel_generator:
        post_updates(count, [100, 1000, 10000, 50000])
        count += 1
        for voter_registration_number in parcel["2020 Absentee Ballot Applicants"].keys():
            registration_number = str(int(voter_registration_number))
            if registration_number in dict_of_confirmed_voters.keys():
                parcel["2020 Absentee Ballot Applicants"][voter_registration_number]["Voted in November 2020"] = True
        write_parcel_list_to_disk([parcel], save_filepath='./parcel_list_temp.txt')

    os.remove("./parcel_list.txt")
    del dict_of_confirmed_voters

    print("\tCreating index connecting registration numbers to voting dates")
    dict_of_registration_numbers = {}
    count = 0
    for voter in voter_generator:
        post_updates(count, [100, 1000, 10000, 50000])
        count += 1
        registration_number = str(int(voter["registration number"]))
        election_date = voter["election date"]
        try:
            dict_of_registration_numbers[registration_number].append(election_date)
        except KeyError:
            dict_of_registration_numbers[registration_number] = [election_date]

    print("\tGetting list of all voters since 2013, and updating parcel data")
    parcel_generator = load_parcel_list_to_memory(save_filepath='./parcel_list_temp.txt', use_as_generator=True)
    for parcel in parcel_generator:
        for voter_registration_number in parcel["2020 Absentee Ballot Applicants"]:
            registration_number = str(int(voter_registration_number))
            try:
                parcel["2020 Absentee Ballot Applicants"][voter_registration_number]["Voter History"] = \
                    dict_of_registration_numbers[registration_number]
            except KeyError:
                continue
        write_parcel_list_to_disk([parcel], save_filepath='./parcel_list.txt')

    os.remove('./parcel_list_temp.txt')
    return True


def update_list_of_voters_with_voter_base_data(parcel_generator=load_parcel_list_to_memory(use_as_generator=True),
                                               voterbase_generator=vb_voter_generator()):
    print("\tIndexing the registration numbers in the Voter Base data file")
    dictionary_of_voter_registrations = {}
    for voter in voterbase_generator:
        registration_number = str(int(voter["REGISTRATION_NUMBER"]))
        registration_date = voter["REGISTRATION_DATE"]
        birth_year = voter["BIRTHDATE"]
        house_number = voter["RESIDENCE_HOUSE_NUMBER"]
        street_name = voter["RESIDENCE_STREET_NAME"]
        city = voter["RESIDENCE_CITY"]
        state = "GA"
        full_address = f"{house_number} {street_name}, {city}, {state}"

        dictionary_of_voter_registrations[registration_number] = {}
        dictionary_of_voter_registrations[registration_number]["Registration Date"] = registration_date
        dictionary_of_voter_registrations[registration_number]["Birth Year"] = birth_year
        dictionary_of_voter_registrations[registration_number]["House Number"] = house_number
        dictionary_of_voter_registrations[registration_number]["Street Name"] = street_name
        dictionary_of_voter_registrations[registration_number]["City"] = city
        dictionary_of_voter_registrations[registration_number]["State"] = state
        dictionary_of_voter_registrations[registration_number]["Full Address"] = full_address

    print("\tAdding Voter Base data to each parcel data point.")
    count = 0
    for parcel in parcel_generator:
        post_updates(count, [1, 10, 100, 1000, 10000, 50000])
        count += 1
        for reg_number in parcel["2020 Absentee Ballot Applicants"].keys():
            registration_number = str(int(reg_number))
            try:
                parcel["2020 Absentee Ballot Applicants"][registration_number]["Voterbase data"] = dictionary_of_voter_registrations[registration_number]
            except KeyError:
                continue
        write_parcel_list_to_disk([parcel], save_filepath="./parcel_list_temp.txt")

    del dictionary_of_voter_registrations
    print("\tDeleting temp file, and reloading data onto main parcel file")
    os.remove("./parcel_list.txt")
    parcel_generator = load_parcel_list_to_memory(save_filepath="./parcel_list_temp.txt", use_as_generator=True)
    for parcel in parcel_generator:
        write_parcel_list_to_disk([parcel], save_filepath="./parcel_list.txt")
    os.remove("./parcel_list_temp.txt")

    return True


def set_up_parcel_list():
    print("Optimizing parcel data for cross referencing against absentee ballot applications.")
    parcel_dictionary = create_dictionary_of_parcel_data()
    print("Finding list of registered voters associated with each address.")
    parcel_dictionary = update_list_of_potential_voters_with_aba_data(parcel_dictionary)
    print("De-optimizing list of parcel data")
    parcel_list = convert_parcel_dictionary_into_parcel_list(parcel_dictionary)
    del parcel_dictionary
    print("Saving parcel list to disk")
    write_parcel_list_to_disk(parcel_list, save_filepath="./parcel_list.txt")
    del parcel_list
    print("Finding list of actual, 2020 election voters at each address.")
    update_list_of_voters_with_voter_history_data()
    print("Updating parcel list with voter base data")
    update_list_of_voters_with_voter_base_data()
    print("Loading parcel list from disk")
    parcel_list = []
    parcel_generator = load_parcel_list_to_memory("./parcel_list.txt", use_as_generator=True)
    for parcel in parcel_generator:
        parcel_list.append(parcel)

    return parcel_list


def simplified_parcel_data(parcel):
    simplified_parcel = {}
    simplified_parcel["Parcel ID"] = parcel["Address Data"]["Parcel ID"]
    simplified_parcel["property class"] = parcel["Address Data"]["Property Class"]
    simplified_parcel["land use code"] = parcel["Address Data"]["Land Use Code"]
    simplified_parcel["Address"] = parcel["Address Data"]["Property Location"].replace("   ", " ") + ", " +\
                                   parcel["Address Data"]["City"]
    try:
        simplified_parcel["seller"] = parcel["Address Data"]["Grantor"]
    except KeyError:
        simplified_parcel["seller"] = ""

    try:
        simplified_parcel["sales date"] = parcel["Address Data"]["Sales Date"]
    except KeyError:
        simplified_parcel["sales date"] = ""

    try:
        num_of_full_baths = int(parcel["Address Data"]["Full Baths"])
    except KeyError:
        num_of_full_baths = 0
    except ValueError:
        num_of_full_baths = 0

    try:
        num_of_half_baths = int(parcel["Address Data"]["Half Baths"])
    except KeyError:
        num_of_half_baths = 0
    except ValueError:
        num_of_half_baths = 0

    try:
        simplified_parcel["number of rooms"] = parcel["Address Data"]["Total Rooms"]
        simplified_parcel["number of bedrooms"] = parcel["Address Data"]["Bedrooms"]
        simplified_parcel["number of bathrooms"] = num_of_half_baths + num_of_full_baths
    except KeyError:
        simplified_parcel["number of rooms"] = 99999
        simplified_parcel["number of bedrooms"] = 99999
        simplified_parcel["number of bathrooms"] = 99999

    try:
        simplified_parcel["number of rooms"] = int(simplified_parcel["number of rooms"])
    except ValueError:
        simplified_parcel["number of rooms"] = 99999
    try:
        simplified_parcel["number of bedrooms"] = int(simplified_parcel["number of bedrooms"])
    except ValueError:
        simplified_parcel["number of bedrooms"] = 99999
    try:
        simplified_parcel["number of bathrooms"] = int(simplified_parcel["number of bathrooms"])
    except ValueError:
        simplified_parcel["number of bathrooms"] = 99999


    voter_registration_numbers = list(parcel['2020 Absentee Ballot Applicants'].keys())
    simplified_parcel["number of 2020 voters"] = 0
    for voter in voter_registration_numbers:
        voted_in_november = parcel['2020 Absentee Ballot Applicants'][voter]["Voted in November 2020"]
        if voted_in_november:
            simplified_parcel["number of 2020 voters"] += 1

    return simplified_parcel


def find_places_with_more_voters_than_bedrooms(parcel_list, multiple_of_num_of_bedrooms=1, multiple_of_num_of_rooms=1,
                                               property_class="", land_use_code=""):
    list_of_suspicious_parcels = []
    for parcel in parcel_list:
        simplified_parcel = simplified_parcel_data(parcel)
        if property_class.lower() not in simplified_parcel["property class"].lower():
            continue
        if land_use_code.lower() not in simplified_parcel["land use code"].lower():
            continue
        num_beds = simplified_parcel["number of bedrooms"]
        num_rooms = simplified_parcel["number of rooms"]
        num_voters = simplified_parcel["number of 2020 voters"]
        if multiple_of_num_of_bedrooms * int(num_beds) < num_voters and multiple_of_num_of_rooms * int(num_rooms) < num_voters:
            #print(parcel_dictionary[street_number][street_name][unit][city])
            list_of_suspicious_parcels.append(simplified_parcel)

    return list_of_suspicious_parcels


def print_list_of_suspicious_parcels(list_of_suspicious_parcels, omitted_keys=["address", "seller", "sales"]):
    for parcel in list_of_suspicious_parcels:
        for key in parcel.keys():
            print_key = True
            for omitted_key in omitted_keys:
                if omitted_key.lower() in key.lower():
                    print_key = False
            if print_key:
                print(f"{key}:\t{parcel[key]}")
        if print_key:
            print("")


def find_parcels_with_infrequent_voter(parcel_list):
    suspicious_parcels = []
    for parcel in parcel_list:
        for voter in parcel["2020 Absentee Ballot Applicants"].keys():
            try:
                parcel["2020 Absentee Ballot Applicants"][voter]["Voterbase data"]
                parcel["2020 Absentee Ballot Applicants"][voter]["Voter History"]
            except KeyError:
                continue
            if not parcel["2020 Absentee Ballot Applicants"][voter]['Voted in November 2020']:
                continue
            if int(parcel["2020 Absentee Ballot Applicants"][voter]["Voterbase data"]["Registration Date"]) < 20150000:
                voted_recently = False
                for vote in parcel["2020 Absentee Ballot Applicants"][voter]["Voter History"]:
                    if "2018" in vote or "2017" in vote or "2016" in vote or "2015" in vote or "2014" in vote:
                        voted_recently = True
                if not voted_recently:
                    suspicious_parcels.append(parcel)

    return suspicious_parcels


if __name__ == "__main__":
    list_of_parcels = set_up_parcel_list()
    suspicious_addresses = find_places_with_more_voters_than_bedrooms(list_of_parcels,
                                                                      multiple_of_num_of_bedrooms=1,
                                                                      multiple_of_num_of_rooms=1)
    print_list_of_suspicious_parcels(suspicious_addresses)