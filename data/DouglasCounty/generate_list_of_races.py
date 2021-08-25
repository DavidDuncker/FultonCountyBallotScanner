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
            ballot = next(ballot_OCR_generator)["lastpage"]
            single_ballot_races = get_single_ballot_races(ballot)
            list_of_races_in_all_ballots.extend(single_ballot_races)
        except StopIteration:
            break
    race_counter = Counter(list_of_races_in_all_ballots)
    sanitized_list_of_races = []
    for race in race_counter.keys():
        if race_counter[race] > 100:
            sanitized_list_of_races.append(race)
    return sanitized_list_of_races


def ballot_generator_douglas_county(ballots):
    for t in ballots.keys():
        for bt in ballots[t].keys():
            for bl in ballots[t][bt].keys():
                ballots[t][bt][bl]["Tabulator"] = t
                ballots[t][bt][bl]["Batch"] = bt
                ballots[t][bt][bl]["Ballot"] = bl

                yield ballots[t][bt][bl]


if __name__ == "__main__":
    pass