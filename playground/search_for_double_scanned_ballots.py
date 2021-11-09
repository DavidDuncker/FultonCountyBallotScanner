from image_analysis import get_ballot_bubble, select_images
import helper_functions
import json
from datetime import datetime
from image_analysis.grids_and_bubbles import ImageProcessingManager as IM

TOP = 0
BOTTOM = 1
LEFT = 2
RIGHT = 3


def count_black_pixels(image_data):
    number_of_rows = image_data.shape[0]
    number_of_columns = image_data.shape[1]
    number_of_black_pixels = 0
    for row in range(0, number_of_rows):
        for column in range(0, number_of_columns):
            pixel_is_black = not (image_data[row][column])
            if pixel_is_black:
                number_of_black_pixels += 1
    return number_of_black_pixels


#This function checks how many extra pixels would need to be added to or subtracted from image 1
# to make it the same width as image 2,
#And also how many extra pixels would need to be added or subtracted for image 1 to have the same height
#Total number of pixel changes are divided by total number of pixels to get a percentage
def check_dimensional_similarity(image_data1, image_data2):
    number_of_rows_in_image_1 = image_data1.shape[0]
    number_of_columns_in_image_1 = image_data1.shape[1]
    number_of_rows_in_image_2 = image_data2.shape[0]
    number_of_columns_in_image_2 = image_data2.shape[1]
    pixel_disparity_for_equal_width = abs(number_of_columns_in_image_2 - number_of_columns_in_image_1)\
                                      *number_of_rows_in_image_1
    pixel_disparity_for_equal_height = abs(number_of_rows_in_image_2 - number_of_rows_in_image_1)\
                                       *number_of_columns_in_image_1
    pixel_disparities = (pixel_disparity_for_equal_width + pixel_disparity_for_equal_height)
    disparity_percentage = pixel_disparities/(number_of_rows_in_image_1 * number_of_columns_in_image_1)
    similarity_percentage = 1 - disparity_percentage
    return similarity_percentage


def get_datetime_difference_in_seconds(first_ballot, second_ballot):
    datetime1 = f"{first_ballot['data']['date']} {first_ballot['data']['time']}"
    datetime1 = datetime1[0:6] + "20" + datetime1[6:]
    datetime1 = datetime.strptime(datetime1, "%m/%d/%Y %H:%M:%S")
    datetime2 = f"{second_ballot['data']['date']} {second_ballot['data']['time']}"
    datetime2 = datetime2[0:6] + "20" + datetime2[6:]
    datetime2 = datetime.strptime(datetime2, "%m/%d/%Y %H:%M:%S")
    time_difference = abs((datetime2 - datetime1).total_seconds())
    return time_difference


def compare_ballot_bubbles(first_ballot_grid, second_ballot_grid, cropping_schemes):
    average_bubble_similarity = 0
    lowest_bubble_similarity = 2
    im = IM()
    for cropping_scheme in cropping_schemes:
        cropped_image_1 = first_ballot_grid.get_grid_image_with_padding(cropping_scheme[TOP],
                                                                        cropping_scheme[BOTTOM],
                                                                        cropping_scheme[LEFT],
                                                                        cropping_scheme[RIGHT],
                                                                        10, 10, 10, 20)
        cropped_image_1 = im.crop_to_content(cropped_image_1)
        cropped_image_2 = second_ballot_grid.get_grid_image_with_padding(cropping_scheme[TOP],
                                                                         cropping_scheme[BOTTOM],
                                                                         cropping_scheme[LEFT],
                                                                         cropping_scheme[RIGHT],
                                                                         10, 10, 10, 20)
        cropped_image_2 = im.crop_to_content(cropped_image_2)
        #Image.fromarray(cropped_image_1).resize( (400, 300) ).show()
        #Image.fromarray(cropped_image_2).resize( (400, 300) ).show()
        percent_similarity_in_pixel_matches = im.compare_two_bubbles(cropped_image_1,
                                                                     cropped_image_2)
        black_pixels_in_first_image = count_black_pixels(cropped_image_1)
        black_pixels_in_second_image = count_black_pixels(cropped_image_2)
        percent_similarity_in_num_black_pixels = abs(black_pixels_in_first_image
                                                     - black_pixels_in_second_image) / \
                                                 black_pixels_in_first_image
        percent_similarity_in_num_black_pixels = 1 - percent_similarity_in_num_black_pixels
        percent_similarity_in_dimensions = check_dimensional_similarity(
            cropped_image_1, cropped_image_2)
        percent_similarity = (percent_similarity_in_pixel_matches
                              + percent_similarity_in_num_black_pixels
                              + percent_similarity_in_dimensions) / 3
        #percent_similarity = (percent_similarity_in_num_black_pixels
        #                      + percent_similarity_in_dimensions) / 2

        #print(f"percent_similarity_in_pixel_matches: {percent_similarity_in_pixel_matches}")
        #print(f"percent_similarity_in_num_black_pixels: {percent_similarity_in_num_black_pixels}")
        #print(f"percent_similarity_in_dimensions: {percent_similarity_in_dimensions}\n\n")
        #                            Image.fromarray(cropped_image_1).resize( (300, 400) ).show()
        #                            Image.fromarray(cropped_image_2).resize( (300, 400) ).show()
        #                            print(f"Percent similarity: {percent_similarity}\n\n")
        average_bubble_similarity += percent_similarity / len(cropping_schemes)
        if percent_similarity < lowest_bubble_similarity:
            lowest_bubble_similarity = percent_similarity
    return lowest_bubble_similarity, average_bubble_similarity


def focus_on_two_particular_ballots(data_directory, ballot_json_filepath, tabulator1, batch1, ballot1,
                                    tabulator2, batch2, ballot2):
    ballot_file = open(ballot_json_filepath, 'r')
    ballots = json.loads(ballot_file.read())[0]
    ballot_file.close()
    list_of_ballots = []
    ballot_index = 17
    first_ballot = {}
    first_ballot["tabulator"] = tabulator1
    first_ballot["batch"] = batch1
    first_ballot["ballot"] = ballot1 #str(ballot_index)
    first_ballot["filepath"] = helper_functions.get_ballot_path(data_directory, first_ballot["tabulator"],
                                                                first_ballot["batch"], first_ballot["ballot"])
    first_ballot["data"] = ballots[first_ballot["tabulator"]][first_ballot["batch"]][first_ballot["ballot"]]
    second_ballot = {}
    second_ballot["tabulator"] = tabulator2
    second_ballot["batch"] = batch2
    second_ballot["ballot"] = ballot2 #str(100 - ballot_index)
    second_ballot["filepath"] = helper_functions.get_ballot_path(data_directory, second_ballot["tabulator"],
                                                                 second_ballot["batch"], second_ballot["ballot"])
    second_ballot["data"] = ballots[second_ballot["tabulator"]][second_ballot["batch"]][second_ballot["ballot"]]
    list_of_ballots.append(first_ballot)
    list_of_ballots.append(second_ballot)
    return list_of_ballots


if __name__ == "__main__":
    data_directory = "/home/dave/Documents/FultonCounty"
    ballot_json_filepath = "../data/FultonCounty/ballot_directory.json"
    list_of_ballots = select_images.select_random_ballots_with_data(data_directory, ballot_json_filepath, 147000)
    image_manager = IM()

    #ballot_parameter = randint(0, 99)
    #list_of_ballots = focus_on_two_particular_ballots(data_directory, ballot_json_filepath, "5162",
    #                                                  "139", str(ballot_parameter), "5162", "147", str(100-ballot_parameter))


    for ballot_index in range(0, len(list_of_ballots)):
        first_ballot = list_of_ballots[ballot_index]
        for second_ballot_index in range(ballot_index+1, len(list_of_ballots)):
            second_ballot = list_of_ballots[second_ballot_index]
            try:
                first_ballot['data']['hash'] == second_ballot['data']['hash']
            except TypeError: #first_ballot_data or second_ballot_data could equal the string "software error"
                continue
            if first_ballot['data']['hash'] == second_ballot['data']['hash'] and \
                    first_ballot['filepath'] != second_ballot['filepath']:
                time_difference = get_datetime_difference_in_seconds(first_ballot, second_ballot)
                if time_difference: # < 200:
                    try:
                        first_ballot_grid_manager = get_ballot_bubble.BallotGridCrops(first_ballot['filepath'])
                        second_ballot_grid_manager = get_ballot_bubble.BallotGridCrops(second_ballot['filepath'])

                        first_ballot_grid = first_ballot_grid_manager.grid
                        second_ballot_grid = second_ballot_grid_manager.grid
                        cropping_schemes_first_page = get_ballot_bubble.get_ballot_bubble_locations(first_ballot)

                        first_page_lowest_bubble_similarity, first_page_average_bubble_similarity = \
                            compare_ballot_bubbles(first_ballot_grid, second_ballot_grid, cropping_schemes_first_page)

                        if first_page_lowest_bubble_similarity > 0.93:
                            #Move on to the second page
                            first_ballot_grid_manager.get_second_page()
                            first_ballot_grid = first_ballot_grid_manager.grid_page_two
                            second_ballot_grid_manager.get_second_page()
                            second_ballot_grid = second_ballot_grid_manager.grid_page_two
                            cropping_schemes_second_page = first_ballot_grid_manager.check_all_second_page_bubbles()
                            second_page_lowest_bubble_similarity, second_page_average_bubble_similarity = \
                                compare_ballot_bubbles(first_ballot_grid, second_ballot_grid, cropping_schemes_second_page)

                            lowest_bubble_similarity = min(first_page_lowest_bubble_similarity,
                                                           second_page_lowest_bubble_similarity)
                            average_bubble_similarity = \
                                (first_page_average_bubble_similarity * len(cropping_schemes_first_page)
                                 + second_page_average_bubble_similarity * len(cropping_schemes_second_page)) / \
                                (len(cropping_schemes_first_page) + len(cropping_schemes_second_page))

                        if lowest_bubble_similarity > 0.93 and average_bubble_similarity > 0.96:
                            print(f"eog {first_ballot['filepath']} &")
                            print(f"eog {second_ballot['filepath']} &")
                            print(f"Lowest similarity: {lowest_bubble_similarity}")
                            print(f"Average similarity: {average_bubble_similarity}")
                            print("\n")
                    except:
                        continue


