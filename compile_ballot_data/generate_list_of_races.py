from collections import Counter
from compile_ballot_data import generate_list_of_races

def get_single_ballot_races(original_text):
    #Get rid of any accidental double, triple, or quadruple linebreaks
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
            single_ballot_races = generate_list_of_races.get_single_ballot_races(ballot)
            list_of_races_in_all_ballots.extend(single_ballot_races)
        except StopIteration:
            break
    race_counter = Counter(list_of_races_in_all_ballots)
    sanitized_list_of_races = []
    for race in race_counter.keys():
        if race_counter[race] > 100:
            sanitized_list_of_races.append(race)
    return sanitized_list_of_races


def get_ballot_candidates(original_text, list_of_races):
    #Get rid of any accidental double, triple, or quadruple linebreaks
    text = original_text.replace("\n\n", "\n")

    #Start text from a certain spot
    bookmark = text.find("President")
    text = text[bookmark:]

    #Remove adjudications
    bookmark = text.find("Adjudicated")
    if bookmark > 0:
        text = text[:bookmark]


    #Split into lines
    lines = text.split("\n")

    candidates = []

    for line_index in range(0, len(lines)):
        if lines[line_index] not in list_of_races:
            candidates.append(lines[line_index])

    return candidates


def get_all_candidates(ballot_generator, list_of_races):
    list_of_candidates_in_all_ballots = []
    for ballot in ballot_generator:
        single_ballot_candidates = get_ballot_candidates(ballot, list_of_races)
        list_of_candidates_in_all_ballots.extend(single_ballot_candidates)
    candidate_counter = Counter(list_of_candidates_in_all_ballots)
    sanitized_list_of_candidates = []
    for candidate in candidate_counter.keys():
        if candidate_counter[candidate] > 50:
            sanitized_list_of_candidates.append(candidate)
    return sanitized_list_of_candidates


def get_all_data(ballot_generator):
    ballots = ballot_generator()
    list_of_races = get_all_races(ballots)

    ballots = ballot_generator()
    list_of_candidates = get_all_candidates(ballots, list_of_races)
    return list_of_races, list_of_candidates


if __name__ == "__main__":
    pass