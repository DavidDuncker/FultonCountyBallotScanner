import csv

PATH = "/home/dave/Documents/Election Fraud/canvass/Election_Ballot_Applications.csv"

def eba_voter_generator(eba_filepath=PATH):
    with open(eba_filepath, errors="replace") as eba_file:
        voterbase_reader = csv.DictReader(eba_file)
        for row in voterbase_reader:
            yield row


def get_dict_of_voters(voterbase_filepath=PATH):
    dict_of_voters = {}
    dict_of_mail_voters = {}
    dict_of_inperson_voters = {}
    voters = eba_voter_generator(voterbase_filepath)
    for voter in voters:
        registration_number = int(voter['Voter Registration'])
        election_date = voter["Election Date"]
        if election_date != "11/03/2020":
            continue
        county = voter['County']
        if county != "FULTON":
            continue
        ballot_status = voter["Ballot Status"]
        if ballot_status != "A":
            continue
        dict_of_voters.update({registration_number: ''})
        ballot_style = voter["Ballot Style"]
        if ballot_style == "MAILED":
            dict_of_mail_voters.update({registration_number: ''})
        elif ballot_style == "IN PERSON" or ballot_style == "ELECTRONIC":
            dict_of_inperson_voters.update({registration_number: ''})

    return dict_of_voters, dict_of_mail_voters, dict_of_inperson_voters
