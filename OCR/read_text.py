import pytesseract
import numpy


def read_text(image_with_data):
    #Read text with image
    output_with_whitespace = pytesseract.image_to_string(image_with_data)
    #Remove all spaces from image for more reliability
    output = output_with_whitespace.replace(" ", "").replace(".", "")
    #Get rid of any accidental double, triple, or quadruple linebreaks
    for i in range(0, 30):
        output = output.replace("\n\n", "\n")

    #Split into lines
    lines = output.split("\n")
    #Create dictionary with all the important attributes of the ballot
    ballot_data = {}

    bookmark1 = lines[0].find("scannedat:")
    bookmark2 = lines[0].find("on")
    ballot_data["filename"] = lines[0][0:bookmark1-3] + "." + lines[0][bookmark1-3:bookmark1]
    # I have no idea why I need to do this, but I do:
    ballot_data["filename"] = ballot_data["filename"].replace("S", "")
    ballot_data["time"] = lines[0][bookmark1+10:bookmark2]
    ballot_data["date"] = lines[0][bookmark2+2:]

    bookmark1 = lines[1].find("Scannedon:")
    bookmark2 = lines[1].find("Tabulator:")
    bookmark3 = lines[1].find("Batch:")
    ballot_data["scanned_on"] = lines[1][bookmark1+10:bookmark2]
    ballot_data["Tabulator"] = lines[1][bookmark2+10:bookmark3]
    ballot_data["Batch"] = lines[1][bookmark3+6:]
    ballot_data["Ballot"] = str(int(ballot_data["filename"][-8:-4]))

    bookmark1 = lines[2].find("PollID:")
    bookmark2 = lines[2].find("BallotID:")
    ballot_data["Poll ID"] = lines[2][bookmark1+7:bookmark2]
    ballot_data["Ballot ID"] = lines[2][bookmark2+9:]

    try: #Assuming that the ballot is a regular, unabridged ballot that displays all races
        ballot_data["President"] = lines[4][:4]
        ballot_data["Senate"] = lines[6][:4]
        ballot_data["Special Senate"] = lines[8][:4]
        ballot_data["PSC1"] = lines[10][:4]
        ballot_data["PSC2"] = lines[12][:4]
        ballot_data["Race6"] = lines[14][:6]
        ballot_data["Race7"] = lines[16][:6]
        ballot_data["Race8"] = lines[18][:6]
        ballot_data["Race9"] = lines[20][:6]
        ballot_data["Race10"] = lines[22][:6]
        ballot_data["Race11"] = lines[24][:6]
        ballot_data["Race12"] = lines[26][:6]
        ballot_data["Race13"] = lines[28][:6]
        ballot_data["Race14"] = lines[30][:6]
        ballot_data["Adjudicated"] = False
        line_that_starts_adjudication = -1
        for line_index in range(0, len(lines)):
            if "Adjudicatedat" in lines[line_index]:
                ballot_data["Adjudicated"] = True
                line_that_starts_adjudication = line_index
        if ballot_data["Adjudicated"]:
            ballot_data["Adjudication"] = {}
            ballot_data["Adjudication"]['time'] = lines[line_that_starts_adjudication][13:19]
            bookmark1 = lines[line_that_starts_adjudication].find("on")
            bookmark2 = lines[line_that_starts_adjudication].find("by")
            ballot_data["Adjudication"]["date"] = lines[line_that_starts_adjudication][bookmark1+2:bookmark2]
            ballot_data["Adjudication"]["adjudicator"] = lines[line_that_starts_adjudication][bookmark2 + 2:]
            ballot_data["Adjudication"]["President"] = lines[line_that_starts_adjudication + 2][:4]
            ballot_data["Adjudication"]["Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["Special Senate"] = lines[line_that_starts_adjudication + 4][:4]
            ballot_data["Adjudication"]["PSC1"] = lines[line_that_starts_adjudication + 6][:4]
            ballot_data["Adjudication"]["PSC2"] = lines[line_that_starts_adjudication + 8][:4]
            ballot_data["Adjudication"]["Race6"] = lines[line_that_starts_adjudication + 10][:6]
            ballot_data["Adjudication"]["Race7"] = lines[line_that_starts_adjudication + 12][:6]
            ballot_data["Adjudication"]["Race8"] = lines[line_that_starts_adjudication + 14][:6]
            ballot_data["Adjudication"]["Race9"] = lines[line_that_starts_adjudication + 16][:6]
            ballot_data["Adjudication"]["Race10"] = lines[line_that_starts_adjudication + 18][:6]
            ballot_data["Adjudication"]["Race11"] = lines[line_that_starts_adjudication + 20][:6]
            ballot_data["Adjudication"]["Race12"] = lines[line_that_starts_adjudication + 22][:6]
            ballot_data["Adjudication"]["Race13"] = lines[line_that_starts_adjudication + 24][:6]
            ballot_data["Adjudication"]["Race14"] = lines[line_that_starts_adjudication + 26][:6]
    except IndexError: #BMD ballots are tricky. Races with no vote are not listed.
        #Assume "Blank Contest" unless a race is specifically listed
        blank_contest = "BLANKC"
        ballot_data["President"] = blank_contest
        ballot_data["Senate"] = blank_contest
        ballot_data["Special Senate"] = blank_contest
        ballot_data["PSC1"] = blank_contest
        ballot_data["PSC2"] = blank_contest
        ballot_data["Race6"] = blank_contest
        ballot_data["Race7"] = blank_contest
        ballot_data["Race8"] = blank_contest
        ballot_data["Race9"] = blank_contest
        ballot_data["Race10"] = blank_contest
        ballot_data["Race11"] = blank_contest
        ballot_data["Race12"] = blank_contest
        ballot_data["Race13"] = blank_contest
        ballot_data["Race14"] = blank_contest
        ballot_data["Adjudicated"] = False
        for line_index in range(0, len(lines)):
            if "President" in lines[line_index]:
                ballot_data["President"] = lines[line_index + 1][:4]
            elif "Perdue" in lines[line_index]:
                ballot_data["Senate"] = lines[line_index + 1][:4]
            elif "Loeffler" in lines[line_index]:
                ballot_data["Special Senate"] = lines[line_index + 1][:4]
            elif "CommissionDistrict1" in lines[line_index]:
                ballot_data["PSC1"] = lines[line_index + 1][:4]
            elif "CommissionDistrict4" in lines[line_index]:
                ballot_data["PSC2"] = lines[line_index + 1][:4]
            elif "HouseDistrict" in lines[line_index]:
                ballot_data["Race6"] = lines[line_index + 1][:6]
            elif "StateSenateDistrict" in lines[line_index]:
                ballot_data["Race7"] = lines[line_index + 1][:6]
            elif "StateHouseDistrict" in lines[line_index]:
                ballot_data["Race8"] = lines[line_index + 1][:6]
            elif "DistrictAttorney" in lines[line_index]:
                ballot_data["Race9"] = lines[line_index + 1][:6]
            elif "SuperiorCourt" in lines[line_index]:
                ballot_data["Race10"] = lines[line_index + 1][:6]
            elif "Sheriff" in lines[line_index]:
                ballot_data["Race11"] = lines[line_index + 1][:6]
            elif "TaxCommissioner" in lines[line_index]:
                ballot_data["Race12"] = lines[line_index + 1][:6]
            elif "Surveyor" in lines[line_index]:
                ballot_data["Race13"] = lines[line_index + 1][:6]
            elif "SolicitorGeneral" in lines[line_index]:
                ballot_data["Race14"] = lines[line_index + 1][:6]

    #Create a single hash to represent the complete, maximally unique data on the entire ballot
    #First, strip all whitespace for maximum reliability
    sanitized_output = "".join(output_with_whitespace.split())
    #Next, strip out all text after the words "Adjudicated at ..." to prevent adjudication from spoiling matches
    bookmark1 = sanitized_output.find("Adjudicatedat")
    sanitized_output = sanitized_output[0:bookmark1]
    #Next, strip out the first two lines to get rid of filename info and datetime info
    bookmark2 = sanitized_output.find("Batch")
    sanitized_output = sanitized_output[bookmark2+9:]
    #Then, strip out all I's, l's, 1's, 0's, O's and punctuation
    #You can't be too careful
    sanitized_output = sanitized_output.replace("I", "").replace("i", "").replace("l", "").replace("1", "")
    sanitized_output = sanitized_output.replace("0", "").replace("O", "")
    sanitized_output = ''.join(filter(str.isalnum, sanitized_output))
    ballot_data["hash"] = hash(sanitized_output)
    return ballot_data


def trim_edges_of_letter(image):
    row = break_down_rows(image)[0]
    column = break_down_columns(image)[0]
    image = image.crop( (column[0]+1, row[0]+1, column[1]-1, row[1]-1) )
    return image


def break_down_rows(image_with_data):
    image_array = numpy.asarray(image_with_data)
    text_rows = []
    current_text_row = []
    currently_selecting_white_space = True
    for row in range(image_array.shape[0]):
        number_of_black_pixels = numpy.count_nonzero(image_array[row, :] == 0)
        if currently_selecting_white_space and number_of_black_pixels > 0:
            current_text_row.append(row-1)
            currently_selecting_white_space = False

        if not currently_selecting_white_space and number_of_black_pixels == 0:
            current_text_row.append(row+1)
            text_rows.append(current_text_row)
            current_text_row = []
            currently_selecting_white_space = True

    return text_rows


def break_down_columns(image_with_data):
    image_array = numpy.asarray(image_with_data)
    text_columns = []
    current_text_column = []
    currently_selecting_white_space = True
    for column in range(image_array.shape[1]):
        number_of_black_pixels = numpy.count_nonzero(image_array[:, column] == 0)
        if currently_selecting_white_space and number_of_black_pixels > 0:
            current_text_column.append(column-1)
            currently_selecting_white_space = False

        if not currently_selecting_white_space and number_of_black_pixels == 0:
            current_text_column.append(column+1)
            text_columns.append(current_text_column)
            current_text_column = []
            currently_selecting_white_space = True

    return text_columns


def get_array_of_letters(image_with_data):
    arrays_of_letters = []
    rows = break_down_rows(image_with_data)
    for row in range(len(rows)):
        arrays_of_letters.append([])
        top = rows[row][0]
        bottom = rows[row][1]
        row_image = image_with_data.crop( (0, top, image_with_data.size[0], bottom ) )
        columns = break_down_columns(row_image)
        for column in range(len(columns)):
            left = columns[column][0]
            right = columns[column][1]
            arrays_of_letters[row].append(image_with_data.crop( (left, top, right, bottom) ))

    return arrays_of_letters


def OCR_array_of_letters(image_with_data):
    array_of_letters = get_array_of_letters(image_with_data)
    final_string = ""

    for row in array_of_letters:
        for letter in row:
            trim_edges_of_letter(letter)
            final_string += pytesseract.image_to_string(letter, lang="eng", config="--psm 10")
        final_string += "\n"

    return final_string