# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from zipfile import ZipFile
from helper_functions import load_configuration_information


#Download ballot images
def download_ballot_images(data_folder, default_download_folder, browser_type):
    print("Opening browser")
    #Open automated browser
    if browser_type == "Chrome":
        automated_browser = webdriver.Chrome()
    elif browser_type == "Firefox":
        automated_browser = webdriver.Firefox()
    print("Loading site")
    #Load site
    automated_browser.get("https://theatlantajournalconstitution.sharefile.com/share/view/"
                          "s3c2d5cda4b5a42a88b6a76990379d181/fo8028b0-c150-45f5-911d-f9959144930e/")

    #Wait until it's loaded
    sleep(2)
    WebDriverWait(automated_browser, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "item_13m21bq")))

    #Get a list of folders in the top directory ("Tabulators")
    print("Getting list of tabulators")
    original_list_of_tabulators = automated_browser.find_elements_by_class_name("item_13m21bq")

    #Click through each folder in the top directory
    for tabulator_number in range(0, len(original_list_of_tabulators)):
        #Get the list of tabulators again. #This is essential for reloading the top directory and avoiding
            #a "stale reference" error
        duplicate_list_of_tabulators = automated_browser.find_elements_by_class_name("item_13m21bq")
        #Save name of top-level folder
        tabulator_name = duplicate_list_of_tabulators[tabulator_number].find_element_by_class_name("name_eol401").text
        print("Looking at " + tabulator_name)
        #Ignore top-level text file
        if "Tabulator" in tabulator_name:
            #Click through top-level folder
            ActionChains(automated_browser).click(duplicate_list_of_tabulators[tabulator_number]).perform()
            #Wait for page to load
            sleep(2)
            WebDriverWait(automated_browser, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item_13m21bq")) )
            #Get a list of lower-level folders ("Batches")
            list_of_batches = automated_browser.find_elements_by_class_name("item_13m21bq")
            for batch in list_of_batches:
                #Scroll into view
                #Important; if an element is accessed without scrolling into view, then its attributes may or may not
                    #be accessible
                ActionChains(automated_browser).move_to_element(batch).perform()
                #Get name of folder
                batch_name = batch.find_element_by_class_name("name_eol401").text
                #Check to see if file has already been added to data collection
                downloaded_data_path = os.path.join(data_folder, tabulator_name, batch_name)
                if os.path.exists(downloaded_data_path):
                    continue
                    #This is BIG. This allows a download to continue where it left off if it fails and is restarted.
                    #And a download WILL fail eventually.
                print("\tLooking at " + batch_name)
                #Click on checkmark
                checkbox = batch.find_element_by_tag_name("label")
                ActionChains(automated_browser).click(checkbox).perform()
                sleep(0.5)
                #Click the download button
                download_button = automated_browser.find_elements_by_xpath("//*[contains(text(), 'Download')]")[0]
                ActionChains(automated_browser).click(download_button).perform()
                #Unclick on checkmark
                sleep(0.5)
                ActionChains(automated_browser).move_to_element(checkbox).click(checkbox).perform()
                print("\t\tDownloading...")
                sleep(10)
                #Check if download finished
                downloaded_zipfile_path = os.path.join(default_download_folder, "Files.zip")
                timer_start = time()
                while not os.path.exists(downloaded_zipfile_path):
                    sleep(5)
                    timer = time()
                    if timer - timer_start > 300:
                        automated_browser.close()
                        raise RuntimeError("Webscraper froze, stopping and starting again...")
                #Unzip downloaded zip file, extract to data directory with folder names as subdirectories
                with ZipFile(downloaded_zipfile_path, 'r') as downloaded_zipfile:
                    downloaded_zipfile.extractall(downloaded_data_path)
                    print("\t\tExtraction to data folder complete")
                    downloaded_zipfile.close()

                #Delete downloaded zipfile
                os.remove(downloaded_zipfile.filename)
                print("\t\tZipFile removed from downloads folder")
                sleep(3)

            #Reload top-level directory
            automated_browser.get("https://theatlantajournalconstitution.sharefile.com/share/view/"
                                  "s3c2d5cda4b5a42a88b6a76990379d181/fo8028b0-c150-45f5-911d-f9959144930e/")

            # Wait until it's loaded
            sleep(2)
            WebDriverWait(automated_browser, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item_13m21bq")))
            sleep(3)

    #Edit configuration file to indicate the download is complete

    #Read
    configuration_file = open(".config", "r")
    list_of_lines = configuration_file.readlines()
    #Edit
    list_of_lines[3] = "True" + os.linesep
    #Write
    configuration_file = open(".config", "w")
    configuration_file.writelines(list_of_lines)
    #Close
    configuration_file.close()
    return(True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #Load configuration data
    data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()

    #Print data for debugging
    print(f"Data directory: {data_directory}")
    print(f"Download directory: {download_directory}")
    print(f"Browser type: {browser_type}")
    print(f"T/F, The data has been downloaded: {data_has_been_downloaded}")

    #Download data if necessary
    if not data_has_been_downloaded:
        while(not data_has_been_downloaded):
            try:
                data_has_been_downloaded = download_ballot_images(data_directory, download_directory, browser_type)
            except RuntimeError:
                #Most likely the webscraper froze. download_ballot_images() will close the browser,
                    #and now we'll just restart the process, picking up where we last left off.
                pass


