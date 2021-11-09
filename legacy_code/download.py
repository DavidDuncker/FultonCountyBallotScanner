# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from zipfile import ZipFile
from helper_functions import load_configuration_information


#Download ballot images
#input: 1) Directory to send downloaded ballots 2) Directory that the ballots are downloaded,
# 3) Browser for Selenium to use.
#Output: True
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
    configuration_file = open("../.config", "r")
    list_of_lines = configuration_file.readlines()
    #Edit
    list_of_lines[3] = "True" + os.linesep
    #Write
    configuration_file = open("../.config", "w")
    configuration_file.writelines(list_of_lines)
    #Close
    configuration_file.close()
    return(True)


#Download ballot images
#input: 1) Directory to send downloaded ballots 2) Directory that the ballots are downloaded,
# 3) Browser for Selenium to use.
#Output: True
def download_ballot_recount_images(data_folder, default_download_folder, browser_type, automated_browser):
    #print("Opening browser")
    ##Open automated browser
    #if browser_type == "Chrome":
    #    automated_browser = webdriver.Chrome()
    #elif browser_type == "Firefox":
    #    automated_browser = webdriver.Firefox()
    print("Loading site")
    #Load site
    automated_browser.get("https://www.dropbox.com/sh/2krd5p5bc6qzurk/AACJ33xWUYEJYR-Rog6I6X9Ya/"
                          "Fulton%20Recount%20Ballot%20Images")

    #Wait until it's loaded
    sleep(2)
    WebDriverWait(automated_browser, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))

    #Scroll down
    for i in range(0, 10):
        ActionChains(automated_browser).send_keys(Keys.END).perform()
        sleep(2)
    ActionChains(automated_browser).send_keys(Keys.HOME).perform()

    #Get a list of folders in the top directory ("Tabulators")
    print("Getting list of tabulators")
    original_list_of_tabulators = automated_browser.find_elements_by_class_name("sl-link--folder")

    #Click through each folder in the top directory
    for tabulator_number in range(0, len(original_list_of_tabulators)):
        #Get the list of tabulators again. #This is essential for reloading the top directory and avoiding
            #a "stale reference" error
        duplicate_list_of_tabulators = automated_browser.find_elements_by_class_name("sl-link--folder")
        #Save name of top-level folder
        tabulator_name = duplicate_list_of_tabulators[tabulator_number].find_element_by_class_name("sl-grid-filename").text
        print("Looking at " + tabulator_name)
        #Ignore top-level text file
        if "Tabulator" in tabulator_name:
            #Click through top-level folder
            ActionChains(automated_browser).move_to_element(duplicate_list_of_tabulators[tabulator_number]).perform()
            ActionChains(automated_browser).click(duplicate_list_of_tabulators[tabulator_number]).perform()
            #Wait for page to load
            sleep(2)
            WebDriverWait(automated_browser, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")) )
            #Scroll down a couple times:
            for i in range(0, 10):
                ActionChains(automated_browser).send_keys(Keys.END).perform()
                sleep(2)
            #Get a list of lower-level folders ("Batches")
            original_list_of_batches = automated_browser.find_elements_by_class_name("sl-link--folder")
            for batch_number in range(0, len(original_list_of_batches)):
                duplicate_list_of_batches = automated_browser.find_elements_by_class_name("sl-link--folder")
                batch = duplicate_list_of_batches[batch_number]
                #Scroll into view
                #Important; if an element is accessed without scrolling into view, then its attributes may or may not
                    #be accessible
                ActionChains(automated_browser).move_to_element(batch).perform()
                # Wait for page to load
                sleep(2)
                WebDriverWait(automated_browser, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
                #Get name of folder
                batch_name = batch.find_element_by_class_name("sl-grid-filename").text
                #Check to see if file has already been added to data collection
                downloaded_data_path = os.path.join(data_folder, tabulator_name, batch_name)
                if os.path.exists(downloaded_data_path):
                    continue
                    #This is BIG. This allows a download to continue where it left off if it fails and is restarted.
                    #And a download WILL fail eventually.
                print("\tLooking at " + batch_name)
                #Click on Folder
                ActionChains(automated_browser).move_to_element(batch).click(batch).perform()
                sleep(2)
                WebDriverWait(automated_browser, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
                sleep(0.5)
                #Click the download button
                download_button = automated_browser.find_element_by_class_name("dig-Button-content")
                ActionChains(automated_browser).click(download_button).perform()
                #Unclick on checkmark
                sleep(0.5)
                print("\t\tDownloading...")
                sleep(10)
                #Check if download finished
                downloaded_zipfile_path = os.path.join(default_download_folder, batch_name + ".zip")
                timer_start = time()
                while not os.path.exists(downloaded_zipfile_path):
                    sleep(5)
                    timer = time()
                    if timer - timer_start > 600:
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

                #Click the "back" button
                automated_browser.back()
                # Wait until it's loaded
                sleep(2)
                WebDriverWait(automated_browser, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
                # Scroll down a couple times:
                for i in range(0, 15):
                    ActionChains(automated_browser).send_keys(Keys.END).perform()
                    sleep(3)
                ActionChains(automated_browser).send_keys(Keys.HOME).perform()

            #Reload top-level directory
            automated_browser.get("https://www.dropbox.com/sh/2krd5p5bc6qzurk/AACJ33xWUYEJYR-Rog6I6X9Ya/"
                                  "Fulton%20Recount%20Ballot%20Images?dl=0&subfolder_nav_tracking=1")

            # Wait until it's loaded
            sleep(2)
            WebDriverWait(automated_browser, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
            sleep(3)

    return(True)


def download_ballot_recount_tab_801_images(data_folder, default_download_folder, browser_type):
    print("Opening browser")
    #Open automated browser
    if browser_type == "Chrome":
        automated_browser = webdriver.Chrome()
    elif browser_type == "Firefox":
        automated_browser = webdriver.Firefox()
    print("Loading site")
    #Load site
    automated_browser.get("https://www.dropbox.com/sh/2krd5p5bc6qzurk/AAChfSapsHS9eaNGvlT7WFh_a/"
                          "Fulton%20Recount%20Ballot%20Images/Tabulator00802/Batch003/Tabulator00801?"
                          "dl=0&subfolder_nav_tracking=1")

    #Wait until it's loaded
    sleep(2)
    WebDriverWait(automated_browser, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))

    #Scroll down to load all batches
    for i in range(0, 15):
        ActionChains(automated_browser).send_keys(Keys.END).perform()
        sleep(1)
    ActionChains(automated_browser).send_keys(Keys.HOME).perform()

    original_list_of_batches = automated_browser.find_elements_by_class_name("sl-link--folder")
    tabulator_name = "Tabulator00801"
    #Get a list of folders in the top directory ("Tabulators")
    print("Getting list of batches")
    for batch_number in range(0, len(original_list_of_batches)):
        duplicate_list_of_batches = automated_browser.find_elements_by_class_name("sl-link--folder")
        batch = duplicate_list_of_batches[batch_number]
        #Scroll into view
        #Important; if an element is accessed without scrolling into view, then its attributes may or may not
            #be accessible
        ActionChains(automated_browser).move_to_element(batch).perform()
        #Wait to load
        sleep(5)
        WebDriverWait(automated_browser, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
        #Get name of folder
        batch_name = batch.find_element_by_class_name("sl-grid-filename").text
        #Check to see if file has already been added to data collection
        downloaded_data_path = os.path.join(data_folder, tabulator_name, batch_name)
        if os.path.exists(downloaded_data_path):
            continue
            #This is BIG. This allows a download to continue where it left off if it fails and is restarted.
            #And a download WILL fail eventually.
        print("\tLooking at " + batch_name)
        #Click on Folder
        ActionChains(automated_browser).move_to_element(batch).click(batch).perform()
        sleep(2)
        WebDriverWait(automated_browser, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
        sleep(0.5)
        #Click the download button
        download_button = automated_browser.find_element_by_class_name("dig-Button-content")
        ActionChains(automated_browser).click(download_button).perform()
        #Unclick on checkmark
        sleep(0.5)
        print("\t\tDownloading...")
        sleep(10)
        #Check if download finished
        downloaded_zipfile_path = os.path.join(default_download_folder, batch_name + ".zip")
        timer_start = time()
        while not os.path.exists(downloaded_zipfile_path):
            sleep(5)
            timer = time()
            if timer - timer_start > 600:
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
        automated_browser.get("https://www.dropbox.com/sh/2krd5p5bc6qzurk/AAChfSapsHS9eaNGvlT7WFh_a/"
                              "Fulton%20Recount%20Ballot%20Images/Tabulator00802/Batch003/Tabulator00801?"
                              "dl=0&subfolder_nav_tracking=1")

        # Wait until it's loaded
        sleep(2)
        WebDriverWait(automated_browser, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sl-link--folder")))
        sleep(3)

        for i in range(0, 15):
            ActionChains(automated_browser).send_keys(Keys.END).perform()
            sleep(1)
        ActionChains(automated_browser).send_keys(Keys.HOME).perform()
    return(True)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while(True):
        try:
            automated_browser = webdriver.Chrome()
            download_ballot_recount_images("/home/dave/Documents/FultonCountyRecount", "/home/dave/Downloads",
                                           "Chrome", automated_browser)
        except:
            automated_browser.close()
            print(sys.exc_info())
            sleep(300)
            continue

    #Load configuration data
    #data_directory, data_has_been_downloaded, browser_type, download_directory = load_configuration_information()

    #Print data for debugging
    #print(f"Data directory: {data_directory}")
    #print(f"Download directory: {download_directory}")
    #print(f"Browser type: {browser_type}")
    #print(f"T/F, The data has been downloaded: {data_has_been_downloaded}")

    #Download data if necessary
    #if not data_has_been_downloaded:
    #    while(not data_has_been_downloaded):
    #        try:
    #            data_has_been_downloaded = download_ballot_images(data_directory, download_directory, browser_type)
    #        except RuntimeError:
    #            #Most likely the webscraper froze. download_ballot_images() will close the browser,
    #                #and now we'll just restart the process, picking up where we last left off.
    #            pass


