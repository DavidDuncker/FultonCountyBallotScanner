import re


def strip_and_sanitize_whitespace(text):
    #Read text with image
    output_with_whitespace = text
    #Remove all spaces from image for more reliability
    output = output_with_whitespace.replace(" ", "").replace(".", "")
    #Get rid of any accidental double, triple, or quadruple linebreaks
    for i in range(0, 30):
        output = output.replace("\n\n", "\n")

    return output


def read_metadata(text):
    metadata = {}

    lines = text.split("\n")

    bookmark1 = lines[0].find("scannedat:")
    bookmark2 = lines[0].find("on")
    metadata["filename"] = text[0:bookmark1-3] + "." + text[bookmark1-3:bookmark1]
    # I have no idea why I need to do this, but I do:
    metadata["filename"] = metadata["filename"].replace("S", "")
    metadata["time"] = lines[0][bookmark1+10:bookmark2]
    metadata["date"] = lines[0][bookmark2+2:]

    bookmark1 = lines[1].find("Scannedon:")
    bookmark2 = lines[1].find("Tabulator:")
    bookmark3 = lines[1].find("Batch:")
    metadata["scanned_on"] = lines[1][bookmark1+10:bookmark2]
    metadata["Tabulator"] = lines[1][bookmark2+10:bookmark3]
    metadata["Batch"] = lines[1][bookmark3+6:]
    metadata["Ballot"] = str(int(metadata["filename"][-8:-4]))

    return metadata


def read_location_data(text):
    location_data = {}

    lines = text.split("\n")
    lines[2] = ''.join(lines[2].split())

    bookmark1 = lines[2].find("PollID:")
    bookmark2 = lines[2].find("BallotID:")
    location_data["Poll ID"] = lines[2][bookmark1+7:bookmark2]
    location_data["Ballot ID"] = lines[2][bookmark2+9:]

    return location_data


def read_race_data(text, list_of_races):
    race_data = {}

    #Remove information about adjudication if necessary
    text_lower = text.lower()
    if "adjudicated" in text_lower:
        bookmark = text_lower.find("adjudicated")
        text = text[:bookmark]

    lines = text.split("\n")

    for line_index in range(0, len(lines)):
        for race in list_of_races:
            race_sanitized = race.replace("5", "S").replace("0", "O").replace("1", "l").replace("8", "B")
            race_sanitized = ''.join(filter(str.isalnum, race_sanitized))
            line_sanitized = lines[line_index].replace("5", "S").replace("0", "O").replace("1", "l").replace("8", "B")
            line_sanitized = ''.join(filter(str.isalnum, line_sanitized))
            if line_sanitized == race_sanitized:
                race_data[race] = lines[line_index+1][:6]

    return race_data


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
    single_line_text_sanitized = single_line_text.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")
    bookmark1 = lines[0].find("at ")
    bookmark2 = lines[0].find(" on ")
    adjudication_data['time'] = lines[0][bookmark1+3 : bookmark2]
    bookmark3 = lines[0].find(" by ")
    adjudication_data["date"] = lines[0][bookmark2+4 : bookmark3]
    adjudication_data["adjudicator"] = lines[0][bookmark3+4 : ]
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

    locations_of_candidate_names = []
    for candidate in list_of_candidates:
        candidate_sanitized = candidate.replace("5", "S").replace("0", "O").replace("1", "l").\
        replace("8", "B").replace("{", "(").replace("}", ")")
        beginning_of_substring = single_line_text_sanitized.find(candidate_sanitized)
        if beginning_of_substring == -1:
            continue
        end_of_substring = beginning_of_substring+len(candidate_sanitized)
        locations_of_candidate_names.append([beginning_of_substring, end_of_substring])



    print(single_line_text)
    print(locations_of_race_names)

    for race_index in range(0, len(locations_of_race_names)):
        race_name_location = locations_of_race_names[race_index]
        race_name = single_line_text[race_name_location[0] : race_name_location[1]]
        next_race_location = locations_of_race_names[race_index + 1]
        candidate_choices = single_line_text[race_name_location[1] : next_race_location[0]]
        def find_races(current_line):
            race = False
            while(race == False):
                break
                #if current_line in list_of_lines_with_race_titles.keys():
                #    race = list_of_lines_with_race_titles[ current_line ]
                #else:
                #    current_line -= 1
                #    if current_line < 0:
                #        return False
            return race
        race = find_races(current_line)
        if race == False:
            continue
        if "*Adjudicated* Write-In" in line:
            adjudication_data[race] = "Write-In"
        elif "*Adjudicated* Vote for" in line:
            bookmark = line.find("for ")
            adjudication_data[race] = line[bookmark + 4:]
        elif ("(NOT COUNTED)" not in line) and len(line) > 7:
            adjudication_data[race] = line

    adjudication_data.update({"adjudicated": True})
    return adjudication_data, True


def get_hash(text):
    #Create a single hash to represent the complete, maximally unique data on the entire ballot
    #First, strip all whitespace for maximum reliability
    text = "".join(text.split())
    #Next, strip out all text after the words "Adjudicated at ..." to prevent adjudication from spoiling matches
    bookmark1 = text.find("Adjudicatedat")
    text = text[0:bookmark1]
    #Next, strip out the first two lines to get rid of filename info and datetime info
    bookmark2 = text.find("Batch")
    text = text[bookmark2+9:]
    #Then, strip out all I's, l's, 1's, 0's, O's and punctuation
    #You can't be too careful
    text = text.replace("I", "").replace("i", "").replace("l", "").replace("1", "")
    text = text.replace("0", "").replace("O", "")
    text = ''.join(filter(str.isalnum, text))
    hash_ = hash(text)

    return hash_


def read_text(text, list_of_races):
    output = strip_and_sanitize_whitespace(text)
    ballot_data = {}
    metadata = read_metadata(output)
    location_data = read_location_data(output)
    race_data = read_race_data(text, list_of_races)
    adjudication_data, ballot_data["adjudicated"] = read_adjudication_data(text, list_of_races)
    hash = get_hash(text)
    ballot_data.update(metadata)
    ballot_data.update(location_data)
    ballot_data.update(race_data)
    ballot_data.update({"adjudication": adjudication_data})
    ballot_data.update({'hash': hash})
    return ballot_data
