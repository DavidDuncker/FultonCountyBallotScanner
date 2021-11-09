import re


def get_locations_of_race_names(text, list_of_races):
    single_line_text = text.replace("\n", "")
    single_line_text = single_line_text.replace("  ", " ")
    single_line_text_sanitized = single_line_text.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")

    locations_of_race_names = []
    for race in list_of_races:
        race_sanitized = race.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")
        #race_sanitized = ''.join(filter(str.isalnum, race_sanitized))
        #line_sanitized = ''.join(filter(str.isalnum, line_sanitized))
        beginning_of_substring = single_line_text_sanitized.find(race_sanitized)
        if beginning_of_substring == -1:
            continue
        end_of_substring = beginning_of_substring+len(race_sanitized)
        locations_of_race_names.append([beginning_of_substring, end_of_substring])

    return locations_of_race_names


def get_locations_of_candidate_names(text, list_of_candidates):
    single_line_text = text.replace("\n", "")
    single_line_text = single_line_text.replace("  ", " ")
    single_line_text_sanitized = single_line_text.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")


    locations_of_candidate_names = []
    for candidate in list_of_candidates:
        candidate_sanitized = candidate.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")
        beginning_of_substring = single_line_text_sanitized.find(candidate_sanitized)
        if beginning_of_substring == -1:
            continue
        end_of_substring = beginning_of_substring+len(candidate_sanitized)
        locations_of_candidate_names.append([beginning_of_substring, end_of_substring])

    return locations_of_candidate_names

def read_adjudication_data(text, list_of_races, list_of_candidates):
    adjudication_data = {}
    #Filter for adjudication data
    text_lower = text.lower()
    if "adjudicated" in text_lower:
        bookmark = text_lower.find("adjudicated")
        text = text[bookmark:]
    else:
        return adjudication_data, False

    mark_percentages = re.findall(r"\(\d{1,3}%\)", text)
    for mark_percentage in mark_percentages:
        text = text.replace(mark_percentage, "")

    lines = text.split("\n")
    single_line_text = text.replace("\n", "")
    single_line_text = single_line_text.replace("  ", " ")
    single_line_text_sanitized = single_line_text.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")
    bookmark1 = lines[0].find("at ")
    bookmark2 = lines[0].find(" on ")
    adjudication_data['time'] = lines[0][bookmark1+3 : bookmark2]
    bookmark3 = lines[0].find(" by ")
    adjudication_data["date"] = lines[0][bookmark2+4 : bookmark3]
    adjudication_data["adjudicator"] = lines[0][bookmark3+4 : ]

    locations_of_race_names = get_locations_of_race_names(text, list_of_races)
    locations_of_candidate_names = get_locations_of_candidate_names(text, list_of_candidates)
    locations_of_race_and_candidate_names = locations_of_race_names + locations_of_candidate_names
    locations_of_race_and_candidate_names.sort()

    for race_index in range(0, len(locations_of_race_names)):
        start_of_substring = locations_of_race_names[race_index][0]
        end_of_substring = locations_of_race_names[race_index][1]
        race_name = single_line_text[start_of_substring, end_of_substring]

        start_of_next_substring = locations_of_race_names[race_index+1][0]
        end_of_next_substring = locations_of_race_names[race_index+1 ][1]



