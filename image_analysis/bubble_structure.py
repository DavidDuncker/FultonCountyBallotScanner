import os
import helper_functions


BLACK = 0
WHITE = 1


def get_bubble_structure(cropped_image_array):
    number_of_rows = cropped_image_array.shape[0]
    number_of_columns = cropped_image_array.shape[1]
    table_of_color_changes = [[] for x in range(0, number_of_columns)]
    for column in range(0, number_of_columns):
        for row in range(0, number_of_rows):
            color_of_current_pixel = cropped_image_array[row][column]
            if row == 0 and color_of_current_pixel == BLACK:
                table_of_color_changes[column].append(0)
            elif row == number_of_rows - 1 and color_of_current_pixel == BLACK:
                table_of_color_changes[column].append(number_of_rows)
            try:
                color_of_previous_pixel = cropped_image_array[row - 1][column]
                if color_of_previous_pixel != color_of_current_pixel:
                    table_of_color_changes[column].append(row)
            except IndexError:
                continue
    return table_of_color_changes


def compare_bubble_structures(table1, table2):
    comparison_score = 0
    max_comparison_score = 0
    buffer = 4
    for column in table1:
        for row in table1[column]:
            #If we're looking at the outer border of the bubble, then set the potential score accordingly
            if row == table1[column][0] or row == table1[column][-1]:
                pixel_comparison_score = 4
                max_pixel_comparison_score = 4
                bubble_border_pixel = True
            else:
                pixel_comparison_score = 10
                max_pixel_comparison_score = 10
                bubble_border_pixel = False
            for column_scan in range(column - buffer, buffer*2):
                for row_scan in range(row - buffer, buffer*2):
                    vertical_distance = abs(table2[column_scan][row_scan] - table1[column][row])
                    horizontal_distance = abs(column - column_scan)
                    distance = max(vertical_distance, horizontal_distance)
                    comparison_score += max_pixel_comparison_score - distance - distance*2*bubble_border_pixel
                    max_comparison_score += max_pixel_comparison_score
    return comparison_score, max_comparison_score

if __name__ == "__main__":
    data_directory, data_has_been_downloaded, browser_type, download_directory = \
        helper_functions.load_configuration_information()
    path1 = os.path.join(data_directory, "Tabulator05162/Batch147/Images/05162_00147_000076.tif")
    path2 = os.path.join(data_directory, "Tabulator05162/Batch139/Images/05162_00139_000024.tif")