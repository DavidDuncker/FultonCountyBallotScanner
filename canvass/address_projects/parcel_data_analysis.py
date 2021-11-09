import json

def load_parcel_data(parcel_path="/home/dave/PycharmProjects/FultonCountyBallotScanner/fully_embellished_parcel_list.txt"):
    list_of_all_parcels = []
    parcel_file = open(parcel_path, 'r')
    for line in parcel_file.readlines():
        list_of_all_parcels.append(json.loads(line))

    return list_of_all_parcels


def standardize_addresses(address):
    address = address.replace(" STREET", " ST")
    address = address.replace(" ROAD", "RD")
    address = address.replace(" COURT", "CT")
    address = address.replace("", "")
    address = address.replace("", "")
    address = address.replace("", "")
    address = address.replace("", "")
    address = address.replace("", "")

    return address

def find_number_of_rooms(parcel):
    parcel_rooms = {}
    try:
        parcel_rooms["seller"] = parcel["Address Data"]["Grantor"]
    except KeyError:
        parcel_rooms["seller"] = ""

    try:
        parcel_rooms["sales date"] = parcel["Address Data"]["Sales Date"]
    except KeyError:
        parcel_rooms["sales date"] = ""

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
        parcel_rooms["number of rooms"] = parcel["Address Data"]["Total Rooms"]
        parcel_rooms["number of bedrooms"] = parcel["Address Data"]["Bedrooms"]
        parcel_rooms["number of bathrooms"] = num_of_half_baths + num_of_full_baths
    except KeyError:
        parcel_rooms["number of rooms"] = 99999
        parcel_rooms["number of bedrooms"] = 99999
        parcel_rooms["number of bathrooms"] = 9999

    try:
        parcel_rooms["number of rooms"] = int(parcel_rooms["number of rooms"])
    except ValueError:
        parcel_rooms["number of rooms"] = 99999
    try:
        parcel_rooms["number of bedrooms"] = int(parcel_rooms["number of bedrooms"])
    except ValueError:
        parcel_rooms["number of bedrooms"] = 99999
    try:
        parcel_rooms["number of bathrooms"] = int(parcel_rooms["number of bathrooms"])
    except ValueError:
        parcel_rooms["number of bathrooms"] = 9999

    return parcel_rooms


def categorize_voters_by_number_of_years_since_voting(parcel):
    parcel_characteristics = {}
    voter_registration_numbers = list(parcel['2020 Absentee Ballot Applicants'].keys())
    parcel_characteristics["number of voters"] = len(voter_registration_numbers)
    parcel_characteristics["number of 2020 voters"] = 0
    parcel_characteristics["years since previous vote"] = []
    for voter in voter_registration_numbers:
        voted_in_november = parcel['2020 Absentee Ballot Applicants'][voter]["Voted in November 2020"]
        if voted_in_november:
            parcel_characteristics["number of 2020 voters"] += 1
            years_voted = parcel['2020 Absentee Ballot Applicants'][voter]["Voter History"]
            years_voted.sort()
            index_of_2020_election = years_voted.index("20201103")
            if index_of_2020_election == 0:
                num_years_since_previous_vote = 8
            else:
                date_of_previous_vote = years_voted[index_of_2020_election - 1]
                year_of_previous_vote = int(date_of_previous_vote[0:4])
                num_years_since_previous_vote = 2020 - year_of_previous_vote
            parcel_characteristics["years since previous vote"].append(num_years_since_previous_vote)

    return parcel_characteristics


def find_number_of_address_mismatches(parcel):
    number_of_address_mismatches = 0
    voter_registration_numbers = list(parcel['2020 Absentee Ballot Applicants'].keys())
    for voter in voter_registration_numbers:
        residential_address = parcel['2020 Absentee Ballot Applicants'][voter]['Residential Address']
        residential_address = standardize_addresses(residential_address)
        mailing_address = parcel['2020 Absentee Ballot Applicants'][voter]['Mailing Address']
        mailing_address = standardize_addresses(mailing_address)
        registration_address = parcel['2020 Absentee Ballot Applicants'][voter]["Voterbase data"]["Full Address"]
        registration_address = standardize_addresses(registration_address)
        if residential_address != mailing_address or mailing_address != registration_address:
            number_of_address_mismatches += 1

    return number_of_address_mismatches


def analyze_parcel(parcel):
    parcel_characteristics = {}
    parcel_characteristics["Parcel ID"] = parcel["Address Data"]["Parcel ID"]
    parcel_characteristics["property class"] = parcel["Address Data"]["Property Class"]
    parcel_characteristics["land use code"] = parcel["Address Data"]["Land Use Code"]
    parcel_characteristics["zoning"] = parcel["Address Data"]["Zoning"]
    parcel_characteristics["Address"] = parcel["Address Data"]["Property Location"].replace("   ", " ") + ", " +\
                                   parcel["Address Data"]["City"]

    parcel_characteristics.update(find_number_of_rooms(parcel))

    parcel_characteristics.update(categorize_voters_by_number_of_years_since_voting(parcel))

    parcel_characteristics["number of address mismatches"] = find_number_of_address_mismatches(parcel)

    return parcel_characteristics


def check_if_parcel_meets_certain_conditions(parcel, min_v_b_r=1, min_v_r_r=1, min_add_mis_ratio=0,
                                             max_add_mis_ratio=2, min_years_since_voted=5):
    parcel_characteristics = analyze_parcel(parcel)
    print(parcel_characteristics)
    conditions_are_met = []
    try:
        voter_to_bedroom_ratio = parcel_characteristics["number of 2020 voters"] / (
                                    parcel_characteristics["number of bedrooms"])
        conditions_are_met.append(voter_to_bedroom_ratio >= min_v_b_r)

        voter_to_non_bathroom_room_ratio = parcel_characteristics["number of 2020 voters"] / \
                                           (parcel_characteristics["number of rooms"] - parcel_characteristics[
                                               "number of bathrooms"])
        conditions_are_met.append(voter_to_non_bathroom_room_ratio >= min_v_r_r)

        conditions_are_met.append(parcel_characteristics["number of address mismatches"] /
                                  parcel_characteristics["number of voters"] >= min_add_mis_ratio)
        conditions_are_met.append(parcel_characteristics["number of address mismatches"] /
                                  parcel_characteristics["number of voters"] <= max_add_mis_ratio)
    except ZeroDivisionError:
        pass

    try:
        conditions_are_met.append(max(parcel_characteristics["years since previous vote"]) >= min_years_since_voted)
    except ValueError:
        pass

    if sum(conditions_are_met) == len(conditions_are_met):
        print(parcel_characteristics)