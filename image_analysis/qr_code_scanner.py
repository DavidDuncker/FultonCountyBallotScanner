from PIL import Image
import numpy as np


def load_image_file(file_path="/home/dave/Documents/Election Fraud/Ballot images/WareCountyImages/Tabulator00130/Batch000/Images/00130_00000_090995.tif"):
    image = Image.open(file_path)
    image_data = np.asarray(image)
    return image_data


def the_row_is_all_white(image_row):
    for pixel in image_row:
        if pixel == 0:
            return False
    return True


def find_groups_of_consecutive_white_rows(image_data):
    number_of_consecutive_white_rows = 0
    start_of_set_of_white_rows = 0
    row_number = 0
    groups_of_white_rows = []
    for image_row in image_data:
        white_row = True
        number_of_black_pixels = 0
        for pixel in image_row:
            if pixel == 0:
                number_of_black_pixels += 1
        if number_of_black_pixels > 10:
            white_row = False

        if white_row == False:
            if number_of_consecutive_white_rows > 0:
                #print(f"Number of consecutive white rows: {number_of_consecutive_white_rows}")
                groups_of_white_rows.append([start_of_set_of_white_rows, row_number])
            number_of_consecutive_white_rows = 0
        if white_row == True:
            if number_of_consecutive_white_rows == 0:
                start_of_set_of_white_rows = row_number
            number_of_consecutive_white_rows += 1
        row_number +=1

    return groups_of_white_rows


def find_qr_code_rows(groups_of_white_rows):
    number_of_large_groups_of_white_rows = 0
    found_second_large_group_of_white_rows = False
    row_containing_start_of_qr_code = 0
    row_containing_end_of_qr_code = 0
    for group in groups_of_white_rows:
        if found_second_large_group_of_white_rows == True:
            row_containing_end_of_qr_code = group[0]
            return row_containing_start_of_qr_code, row_containing_end_of_qr_code
        number_of_white_rows = group[1] - group[0]
        if number_of_white_rows > 75:
            number_of_large_groups_of_white_rows += 1
        if number_of_large_groups_of_white_rows == 2:
            row_containing_start_of_qr_code = group[1]
            found_second_large_group_of_white_rows = True

    return -1, -1


def find_qr_code_columns(image_data):
    list_of_non_empty_columns = []
    start_of_group_of_non_empty_columns = -1
    end_of_group_of_non_empty_columns = -1
    for column in range(0, len(image_data[0])):
        number_of_black_pixels = 0
        for pixel in image_data[:,column]:
            if pixel == 0:
                number_of_black_pixels += 1

        if number_of_black_pixels > 5:
            if start_of_group_of_non_empty_columns == -1:
                start_of_group_of_non_empty_columns = column
        elif number_of_black_pixels <= 5:
            if start_of_group_of_non_empty_columns > -1:
                end_of_group_of_non_empty_columns = column
                #print(end_of_group_of_non_empty_columns)
                if end_of_group_of_non_empty_columns - start_of_group_of_non_empty_columns > 100:
                    list_of_non_empty_columns.append([start_of_group_of_non_empty_columns, end_of_group_of_non_empty_columns])
            start_of_group_of_non_empty_columns = -1

    #print(f"\n\n{list_of_non_empty_columns[0][0]}, {list_of_non_empty_columns[0][1]}")
    return list_of_non_empty_columns[0][0], list_of_non_empty_columns[0][1]


def isolate_qr_code(file_path="/home/dave/Documents/Election Fraud/Ballot images/WareCountyImages/Tabulator00130/"
                                "Batch000/Images/00130_00000_090995.tif"):
    print("Loading image.")
    image_data = load_image_file(file_path)
    print("Finding rows with the QR code")
    groups_of_white_rows = find_groups_of_consecutive_white_rows(image_data)
    row_containing_start_of_qr_code, row_containing_end_of_qr_code = find_qr_code_rows(groups_of_white_rows)
    print("Finding columns with the QR code")
    column_containing_start_of_qr_code, column_containing_end_of_qr_code = \
        find_qr_code_columns(image_data[row_containing_start_of_qr_code: row_containing_end_of_qr_code])
    print("About to return the cropped QR code")
    cropped_image_data = image_data[row_containing_start_of_qr_code-10: row_containing_end_of_qr_code+10,
                         column_containing_start_of_qr_code-10: column_containing_end_of_qr_code+10]
    #Image.fromarray(cropped_image_data).show()
    return cropped_image_data


def find_number_of_color_transitions_below_each_row(image_data):
    list_of_color_transitions_after_rows = []
    for row_number in range(0, len(image_data[:,0]) - 2):
        list_of_color_transitions_after_row_pixel = []
        for pixel in range(0, len(image_data[row_number,:]) - 2):
            if image_data[row_number, pixel] != image_data[row_number + 1, pixel]:
                list_of_color_transitions_after_row_pixel.append(pixel)
        list_of_color_transitions_after_rows.append(list_of_color_transitions_after_row_pixel)
    return list_of_color_transitions_after_rows


def find_number_of_color_transitions_right_of_each_column(image_data):
    list_of_color_transitions_after_columns = []
    for column_number in range(0, len(image_data[0, :]) - 2):
        list_of_color_transitions_after_column_pixel = []
        for pixel in range(0, len(image_data[:, column_number]) - 2):
            if image_data[pixel, column_number] != image_data[pixel, column_number + 1]:
                list_of_color_transitions_after_column_pixel.append(pixel)
        list_of_color_transitions_after_columns.append(list_of_color_transitions_after_column_pixel)
    return list_of_color_transitions_after_columns


def find_distorted_qr_rows_and_columns(color_transitions_in_each_row, color_transitions_in_each_column):
    rows_on_the_qr_grid = []
    for pixel_column_number in range(1, len(color_transitions_in_each_row) - 1):
        if color_transitions_in_each_row[pixel_column_number] > color_transitions_in_each_row[pixel_column_number + 1] and \
                color_transitions_in_each_row[pixel_column_number] > color_transitions_in_each_row[pixel_column_number - 1]:
            rows_on_the_qr_grid.append(pixel_column_number)

    columns_on_the_qr_grid = []
    for pixel_column_number in range(1, len(color_transitions_in_each_column) - 1):
        if color_transitions_in_each_column[pixel_column_number] > color_transitions_in_each_column[pixel_column_number + 1] and \
                color_transitions_in_each_column[pixel_column_number] > color_transitions_in_each_column[pixel_column_number - 1]:
            columns_on_the_qr_grid.append(pixel_column_number)

    return rows_on_the_qr_grid, columns_on_the_qr_grid


def demonstrate_location_of_qr_rows_and_columns(qr_image, rows_on_the_qr_grid, columns_on_the_qr_grid):
    for row in rows_on_the_qr_grid:
        for pixel in range(0, len(qr_image[row,:]) ):
            qr_image[row, pixel] = 0

    for column in columns_on_the_qr_grid:
        for pixel in range(0, len(qr_image[:, column]) ):
            qr_image[pixel, column] = 0

    return qr_image



def read_distorted_qr_code(file_path="/home/dave/Documents/Election Fraud/Ballot images/WareCountyImages/Tabulator00130/"
                                "Batch000/Images/00130_00000_090995.tif"):
    qr_code_image = isolate_qr_code(file_path)
    print("Finding color transitions in each row:")
    color_transitions_in_each_row = find_number_of_color_transitions_below_each_row(qr_code_image)
    print("Finding color transitions in each column:")
    color_transitions_in_each_column = find_number_of_color_transitions_right_of_each_column(qr_code_image)
    return color_transitions_in_each_row, color_transitions_in_each_column
    rows_on_the_qr_grid, columns_on_the_qr_grid = \
        find_distorted_qr_rows_and_columns(color_transitions_in_each_row, color_transitions_in_each_column)
    modified_qr_code_image = demonstrate_location_of_qr_rows_and_columns(qr_code_image,
                                                                         rows_on_the_qr_grid, columns_on_the_qr_grid)
    Image.fromarray(modified_qr_code_image).resize( (1000, 1000) ).show()
    return modified_qr_code_image