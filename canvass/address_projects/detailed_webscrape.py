import json

import lxml
from lxml import html

import requests

import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from time import sleep

# The webdriver will be a global variable
driver = None
actionChainsDriver = None


def initiate_browser():
    options = webdriver.ChromeOptions()

    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    actionChainsDriver = ActionChains(driver)

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    options = webdriver.ChromeOptions()

    options.headless = True
    options.add_argument('user-agent={' + user_agent + '}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--initiate_browser-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    driver.get("https://iaspublicaccess.fultoncountyga.gov/search/commonsearch.aspx?mode=parid")
    try:
        agree_button_element = driver.find_element_by_id("btAgree")
        actionChainsDriver.move_to_element(agree_button_element).click().perform()
    except selenium.common.exceptions.NoSuchElementException:
        pass


def get_URL(parcel_ID):
    url_safe_parcel_ID = parcel_ID.replace(" ", "%20")
    url = f"https://iaspublicaccess.fultoncountyga.gov/Datalets/PrintDatalet.aspx?pin={url_safe_parcel_ID}&gsp=PROFILEALL&taxyear=2021&jur=000&ownseq=0&card=1&roll=RE&State=1&item=1&items=-1&all=all&ranks=Datalet"
    return url


def scrape_parcel_data_with_selenium(parcel_ID):
    url = get_URL(parcel_ID)
    print(f"URL: \t{url}")
    driver.get(url)
    driver_pause_event = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'DataletSideHeading')))

    list_of_data_attributes__elements = driver.find_elements_by_xpath("//td[@class='DataletSideHeading']")
    list_of_data_values__elements = driver.find_elements_by_xpath(
        "//td[@class='DataletSideHeading']/following-sibling::td[@class='DataletData']")
    dictionary_of_property_data = {'Parcel ID': parcel_ID}
    for i in range(0, len(list_of_data_attributes__elements)):
        dictionary_of_property_data[list_of_data_attributes__elements[i].text.strip(':')] = list_of_data_values__elements[i].text
        for key, value in dictionary_of_property_data:
            print(f"{key}: {value}")

    return dictionary_of_property_data


def write_to_log(logtext):
    with open('detailed_webscrape_log.txt', 'a') as logfile:
        logfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\t' + logtext + '\n')
        print(logtext)
    return


def write_detailed_parcel_data_to_disk(detailed_parcel_dictionary):
    with open('detailed_webscrape_data.txt', 'a') as data_storage:
        data_storage.write(json.dumps(detailed_parcel_dictionary) + '\n')
    with open("already_scraped_parcel_IDs.txt", "a") as already_scraped_parcel_ids:
        already_scraped_parcel_ids.write(detailed_parcel_dictionary["Parcel ID"] + '\n')


def scrape_parcel_data_with_requests_module(parcel_ID):
    write_to_log(f"Scraping {parcel_ID}")
    url = get_URL(parcel_ID)

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    headers = {"User-Agent": user_agent}
    url_HTML_request = requests.get(url, headers=headers)
    HTML_response = url_HTML_request.text

    if "We are currently conducting maintenance on the" in HTML_response:
        write_to_log("Site is under maintenance. Waiting an hour.")
        return "maintenance"

    try:
        HTML_tree_structure = html.fromstring(HTML_response)
    except lxml.etree.ParserError:
        return -1

    list_of_data_attributes = [attribute for attribute in HTML_tree_structure.xpath("//td[@class='DataletSideHeading']")]
    list_of_data_values = [value for value in HTML_tree_structure.xpath("//td[@class='DataletSideHeading']/following-sibling::td[@class='DataletData']")]

    dictionary_of_property_data = {'Parcel ID': parcel_ID}
    for i in range(0, len(list_of_data_attributes)):
        dictionary_of_property_data[list_of_data_attributes[i].text.strip(':')] = \
        list_of_data_values[i].text
        #for key, value in dictionary_of_property_data.items():
        #    print(f"{key}: {value}")

    if len(list_of_data_attributes) == 0:
        write_to_log("Possible server timeout. Sleeping for 3 minutes")
        sleep(60*3)
        dictionary_of_property_data = scrape_parcel_data_with_requests_module(parcel_ID)

    write_detailed_parcel_data_to_disk(dictionary_of_property_data)
    return dictionary_of_property_data


def load_list_of_parcel_ids(filepath_with_basic_data_on_parcels="property_webscrape_parcel_basics.txt"):
    write_to_log("About to load list of parcel IDs")
    parcel_data_file = open(filepath_with_basic_data_on_parcels, 'r')
    dictionary_with_parcel_IDs_as_keys = {} #Use dictionary keys to remove duplicates
    for line in parcel_data_file.readlines():
        sanitized_line = line.replace("{'", '{"').replace("': '", '": "').replace("', '", '", "').replace("'}", '"}').replace(
            "\", '", '", "').replace("\": '", '": "').replace("': \"", '": "')
        parcel_id = json.loads(sanitized_line)["Parcel ID"]
        dictionary_with_parcel_IDs_as_keys.update({parcel_id: None})
    write_to_log("Loaded list of parcel IDs, about to sort")
    list_of_parcel_IDs = list(dictionary_with_parcel_IDs_as_keys.keys())
    list_of_parcel_IDs.sort()
    write_to_log("Sorted parcel IDs")
    return list_of_parcel_IDs


def load_list_of_already_scraped_parcel_IDs(filepath_of_already_scraped_parcel_IDs="already_scraped_parcel_IDs.txt"):
    write_to_log("Loading list of already scraped parcel IDs")
    list_of_already_scraped_parcel_IDs = []
    parcel_file = open(filepath_of_already_scraped_parcel_IDs, 'r')
    for parcel_ID in parcel_file.readlines():
        list_of_already_scraped_parcel_IDs.append(parcel_ID.strip())
    write_to_log("About to sort parcel IDs")
    list_of_already_scraped_parcel_IDs.sort()
    write_to_log("Sorted parcel IDs")
    return list_of_already_scraped_parcel_IDs


def add_space_to_beginning_of_Ls(parcel_ID):
    location_of_Ls = parcel_ID.find("LL")
    if location_of_Ls != -1:
        parcel_ID = " ".join((parcel_ID[0:location_of_Ls], parcel_ID[location_of_Ls:]))
    return parcel_ID


def turn_list_into_dictionary_keys_for_efficiency(list):
    dictionary = {}
    for item in list:
        dictionary.update({item: None})
    return dictionary


if __name__ == "__main__":
    list_of_parcel_IDs = load_list_of_parcel_ids()
    try:
        already_scraped_parcel_IDs = load_list_of_already_scraped_parcel_IDs()
    except FileNotFoundError:
        write_to_log("Creating a file to hold list of already-scraped parcel IDs")
        already_scraped_parcel_IDs = []
        new_file = open("already_scraped_parcel_IDs.txt", 'w')
        new_file.write("")
        new_file.close()

    write_to_log(f"Number of parcel IDs loaded: {len(list_of_parcel_IDs)}")
    write_to_log(f"Number of already scraped parcel IDs: {len(already_scraped_parcel_IDs)}")
    dict_of_scraped_parcel_IDs = turn_list_into_dictionary_keys_for_efficiency(already_scraped_parcel_IDs)

    for parcel_ID in list_of_parcel_IDs:
        parcel_ID = add_space_to_beginning_of_Ls(parcel_ID)
        if parcel_ID in dict_of_scraped_parcel_IDs.keys():
            continue
        succeeded_in_scraping = False
        number_of_connection_attempts = 0
        while(not succeeded_in_scraping):
            try:
                results = scrape_parcel_data_with_requests_module(parcel_ID)
                if results == "maintenance":
                    sleep(3600)
                else:
                    succeeded_in_scraping = True
            except:
                write_to_log("Possible server timeout. Sleeping for 3 minutes")
                sleep(60 * 3)
                succeeded_in_scraping = False
                number_of_connection_attempts += 1
                if number_of_connection_attempts == 4:
                    break
        sleep(0)
