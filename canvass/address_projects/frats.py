from canvass import voterbase
from canvass import eba_statewide


def sanitize_street_name(street_name):
    street_name = street_name.replace("FIRST", "1ST")
    street_name = street_name.replace("SECOND", "2ND")
    street_name = street_name.replace("THIRD", "3RD")
    street_name = street_name.replace("FOURTH", "4TH")
    street_name = street_name.replace("FIFTH", "5TH")
    street_name = street_name.replace("SIXTH", "6TH")
    street_name = street_name.replace("SEVENTH", "7TH")
    street_name = street_name.replace("EIGHTH", "8TH")
    street_name = street_name.replace("NINTH", "9TH")
    street_name = street_name.replace("TENTH", "10TH")

    return street_name


def generate_address_info():
    list_of_voters = {}
    fraternity_list_path = "/home/dave/Documents/Election Fraud/GreekAngle/AtlantaFrats.txt"
    fraternity_list_file = open(fraternity_list_path, 'r')
    fraternity_list = {}
    file_lines = fraternity_list_file.readlines()
    for line_index in range(0, len(file_lines)):
        if line_index % 3 == 0:
            frat_name = file_lines[line_index].replace("\n", "")
        if line_index % 3 == 1:
            frat_address = file_lines[line_index].replace("\n", "")
            frat_address = sanitize_street_name(frat_address)
            frat_address = frat_address.upper()
            fraternity_list.update({frat_name: frat_address})
    voter_generator = voterbase.voterbase_voter_generator()
    for voter in voter_generator:
        registration_number = int(voter["REGISTRATION_NUMBER"])
        name = f"{voter['FIRST_NAME']} {voter['MIDDLE_MAIDEN_NAME']} {voter['LAST_NAME']}"
        street_number = voter["RESIDENCE_HOUSE_NUMBER"]
        street_name = sanitize_street_name(voter["RESIDENCE_STREET_NAME"])
        street_suffix = voter["RESIDENCE_STREET_SUFFIX"]
        city = voter["RESIDENCE_CITY"]
        zip_code = voter["RESIDENCE_ZIPCODE"]
        birthdate = voter["BIRTHDATE"]
        last_voted = voter["DATE_LAST_VOTED"]
        registration_date = voter["REGISTRATION_DATE"]
        for frat_name in fraternity_list.keys():
            frat_address = fraternity_list[frat_name]
            frat_street_number = frat_address.split(" ")[0]
            frat_street_name = " ".join(frat_address.split(",")[0].split(" ")[1:])
            frat_city = frat_address.split(",")[1].replace(" ", "")
            frat_zip = frat_address.split(",")[2].split(" ")[-1]
            if street_number in frat_street_number and street_name in frat_street_name and \
                    street_suffix in frat_street_name and city in frat_city and zip_code in frat_zip\
                    and birthdate<="1997":
                update_data = {registration_number: [frat_name, name, f"{street_number} {street_name} {street_suffix}, "
                                                                      f"{city}, GA {zip_code}", birthdate, last_voted,
                                                     registration_date]}
                print(update_data)
                list_of_voters.update(update_data)

    return list_of_voters


def search_through_ballot_applications():
    list_of_results = []
    header = "Registration Number;; Name according to VoterBase; Name according to Ballot Application dataset; " \
             "Name of residing fraternity; " \
             "Address according to VoterBase; Address according to Ballot Application dataset;; " \
             "Birth year according to VoterBase; Registration date according to VoterBase; " \
             "Date of last vote according to VoterBase;;" \
             "Ballot Application Date according to Ballot Application dataset;" \
             "Ballot Issued Date according to Ballot Application dataset;" \
             "Ballot Return Date according to Ballot Application dataset;" \
             "Ballot Status; Ballot Style"
    list_of_results.append(header)
    ballot_applications = eba_statewide.eba_voter_generator()
    dictionary_of_voters = generate_address_info()
    print(header)
    for ballot in ballot_applications:
        ballot_registration_number = int(ballot['Voter Registration #'])
        if ballot_registration_number not in dictionary_of_voters.keys():
            continue
        ballot_status = ballot["Ballot Status"]
        ballot_style = ballot["Ballot Style"]
        app_date = ballot['Application Date']
        issued_date = ballot['Ballot Issued Date']
        return_date = ballot['Ballot Return Date']
        ballot_address = f"{ballot['Street #']} {ballot['Street Name']} {ballot['Apt/Unit']}, {ballot['City']}, GA {ballot['Zip Code']}"
        ballot_name = f"{ballot['First Name']} {ballot['Middle Name']} {ballot['Last Name']}"
        voterbase_data = dictionary_of_voters[ballot_registration_number]
        frat_name = voterbase_data[0]
        voterbase_name = voterbase_data[1]
        voterbase_address = voterbase_data[2]
        birthyear = voterbase_data[3]
        voterbase_last_voted = voterbase_data[4]
        registration_date = voterbase_data[5]
        voter_data = [ballot_registration_number, "", voterbase_name, ballot_name, frat_name,
                      voterbase_address, ballot_address, "", birthyear,
                      registration_date, voterbase_last_voted, "", app_date,
                      issued_date, return_date, ballot_status, ballot_style]
        voter_data = list(map(str, voter_data))
        voter_data_string = ";".join(voter_data)
        print(voter_data_string)
        list_of_results.append(voter_data_string)
    return list_of_results
