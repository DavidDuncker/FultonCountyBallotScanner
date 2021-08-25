import OCR
from collections import Counter

def get_single_ballot_races(original_text):
    #Get rid of any accidental double, triple, or quadruple linebreaks
    for i in range(0, 30):
        text = original_text.replace("\n\n", "\n")

    #Start text from a certain spot
    bookmark = text.find("President")
    text = text[bookmark:]

    #Get rid of adjudications and overvotes
    if "OVER-VOTE" in text or "Adjudicated" in text:
        return []

    #Split into lines
    lines = text.split("\n")

    races = []

    for line_index in range(0, len(lines)):
        if line_index % 2 == 0 and \
                ("write-in" not in lines[line_index].lower()) and \
                '\x0c' not in lines[line_index]:
            races.append(lines[line_index])

    return races


def get_all_races(ballot_OCR_generator):
    list_of_races_in_all_ballots = []
    while (True):
        try:
            ballot = next(ballot_OCR_generator)
            single_ballot_races = OCR.generate_list_of_races.get_single_ballot_races(ballot[1])
            list_of_races_in_all_ballots.extend(single_ballot_races)
        except StopIteration:
            break
    race_counter = Counter(list_of_races_in_all_ballots)
    sanitized_list_of_races = []
    for race in race_counter.keys():
        if race_counter[race] > 100:
            sanitized_list_of_races.append(race)
    return sanitized_list_of_races



def get_dictionary_of_races(location):
    #['President of the United States', 'US Senate (Perdue)', 'US Senate (Loeffler) - Special',
# 'Public Service Commission District 1', 'Public Service Commission District 4', 'US House District 13',
# 'State Senate District 35', 'State House District 64', 'District Attorney - Atlanta', 'Clerk of Superior Court',
# 'Sheriff', 'Tax Commissioner', 'Surveyor', 'Solicitor General', 'County Commission District 6',
# 'Soil and Water - Fulton County', 'Constitutional Amendment #1', 'Constitutional Amendment #2',
# 'Statewide Referendum A', '\x0c', 'Joseph R. Biden (Dem)', 'Jon Ossoff (Dem)', 'Raphael Warnock (Dem)',
# 'Robert G. Bryant (Dem)', 'Daniel Blackman (Dem)', 'David Scott (I) (Dem)', 'Jo Anna Potts', 'Debra Bazemore (I) (Dem)', 'Fani Willis (Dem)', 'Cathelene "Tina" Robinson (I) (Dem)']
    races = {}

if __name__ == "__main__":
    pass