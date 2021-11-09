import canvass.comparisons.pattern_search as pattern_search
import canvass.voterbase as voterbase

def wtf_voter_base(list_of_excluded_voters):
    missing_voters = list_of_excluded_voters['statewide/all voters'][
        'Voter History voters not in Voter Base\'s list of voters']
    voter_history__missing_voters = pattern_search.missing_voter_data_generator(missing_voters, "Voter History")
    columns_of_interest = ["COUNTY_CODE", "REGISTRATION_NUMBER", "VOTER_STATUS", "BIRTHDATE", "REGISTRATION_DATE"]
    for voterhistory_voter in voter_history__missing_voters:
        voterbase_generator = voterbase.voterbase_voter_generator()
        vh_registration_number = int(voterhistory_voter['registration number'])
        print("Voter History File Entry:")
        print(voterhistory_voter)
        print(f"Voter Base Entries with registration numbers close to {vh_registration_number}:")
        for voterbase_voter in voterbase_generator:
            vb_registration_number = int(voterbase_voter["REGISTRATION_NUMBER"])
            if abs(vh_registration_number - vb_registration_number) < 5:
                printable_data = ""
                for key in voterbase_voter.keys():
                    if key in columns_of_interest:
                        printable_data += f"{key}:  {voterbase_voter[key]}\t"
                print(f"\t\t{voterbase_voter}")
                #print(f"\t{printable_data}")
            if vb_registration_number - vh_registration_number > 5:
                print("\n")
                break





def compile_missing_VoterBase_voters_by_county(list_of_excluded_voters):
    missing_voters = list_of_excluded_voters['statewide/all voters']['Voter History voters not in Voter Base\'s list of voters']
    voter_history__missing_voters = pattern_search.missing_voter_data_generator(missing_voters, "Voter History")

    missing_voters_by_county = {}
    for missing_voter in voter_history__missing_voters:
        try:
            missing_voters_by_county[missing_voter["county"]] += 1
        except KeyError:
            missing_voters_by_county[missing_voter["county"]] = 1

    return missing_voters_by_county