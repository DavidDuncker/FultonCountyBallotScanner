import os


def load_configuration_information():
    try:
        #Open configuration file
        configuration_file = open(".config", 'r')
    except FileNotFoundError:
        #Create configuration file with input from user
        configuration_file = open(".config", 'w')

        new_configuration_file_contents = ""
        new_configuration_file_contents += "Directory for downloaded data (no quotations, please): " + os.linesep
        new_configuration_file_contents += input("Enter the directory for the downloaded data (no quotes): "
                                                 + os.linesep) + os.linesep
        new_configuration_file_contents += "Have the files been downloaded completely? " + os.linesep
        new_configuration_file_contents += "False" + os.linesep
        new_configuration_file_contents += "Selenium Webdriver: Chrome or Firefox?: " + os.linesep
        new_configuration_file_contents += input("You need to install Selenium Webdriver to download the data; Will you "
                                                 "use Firefox or Chrome?"  + os.linesep).capitalize() + os.linesep
        new_configuration_file_contents += "Download folder to search for downloaded data: " + os.linesep
        new_configuration_file_contents += input("Now what is your selenium browser's default "
                                                 "download folder? " + os.linesep) + os.linesep

        configuration_file.write(new_configuration_file_contents)
        configuration_file.close()
        configuration_file = open(".config", 'r')

    all_lines_in_file = configuration_file.readlines()
    data_directory = all_lines_in_file[1].strip()
    data_has_been_downloaded = all_lines_in_file[3].strip() != "False" #Only way to convert string to bool
    browser_type = all_lines_in_file[5].strip()
    download_directory = all_lines_in_file[7].strip()
    return data_directory, data_has_been_downloaded, browser_type, download_directory