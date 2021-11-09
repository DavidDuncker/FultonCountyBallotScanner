import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
import sys

# The webdriver will be a global variable
options = webdriver.ChromeOptions()

prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
actionChainsDriver = ActionChains(driver)

#This variable will control whether we do a quick scrape or a detailed scrape
willDoADetailedSearch = False


def initiate_browser():
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


def execute_search_query(parcel_id_search_term):
    sleep(2)
    parcel_id_input_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'inpParid')))
    actionChainsDriver.move_to_element(parcel_id_input_element)
    parcel_id_input_element.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
    parcel_id_input_element.send_keys(parcel_id_search_term)
    submit_button_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'btSearch')))
    actionChainsDriver.move_to_element(submit_button_element)
    submit_button_element.click()


def find_number_of_search_results():
    # Check the number of search results, make sure it's under 250
    # Note, if it is less than 250, then "Total found: " is not displayed
    number_of_results_location_1 = driver.page_source.find("Total found: ") + 13
    number_of_results_location_2 = driver.page_source.find(" records")
    number_of_results = driver.page_source[number_of_results_location_1: number_of_results_location_2]

    return number_of_results


def find_number_of_search_results2():
    # Use this one if there are less than 250 results
    # return z where z is from 'Displaying x to y of z'
    too_many_results_location_1 = driver.page_source.find("Displaying")
    if (too_many_results_location_1 < 0):
        return '0'  # There are no results
    too_many_results_location_2 = driver.page_source.find("of", too_many_results_location_1)
    too_many_results_location_3 = driver.page_source.find("<b>", too_many_results_location_2)
    too_many_results_location_4 = driver.page_source.find("<b>", too_many_results_location_3)
    too_many_results_location_5 = driver.page_source.find("</b>", too_many_results_location_4)
    str1 = driver.page_source[too_many_results_location_4 + 4: too_many_results_location_5].strip()
    return str1


def too_many_results():
    # If 'Displaying x to y of z' where z is 250 then there are too many results
    too_many_results_location_1 = driver.page_source.find("Displaying")
    if (too_many_results_location_1 < 0):
        return -1  # There are no results
    too_many_results_location_2 = driver.page_source.find("of", too_many_results_location_1)
    too_many_results_location_3 = driver.page_source.find("<b>", too_many_results_location_2)
    too_many_results_location_4 = driver.page_source.find("<b>", too_many_results_location_3)
    too_many_results_location_5 = driver.page_source.find("</b>", too_many_results_location_4)
    str1 = driver.page_source[too_many_results_location_4 + 4: too_many_results_location_5].strip()
    if (int(str1) == 250):
        # print('250 or more records, 250 results')
        return 1  # There are too many results
    else:
        # print(str1 + ' results')
        return 0  # There are a good number of results for collection


def collect_search_results_on_page(detailed):
    sleep(0)
    # Grab all the data in the table, and print it out
    element__table_of_results = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'searchResults')))
    parsed_results = []

    while (1):
        # Needed to move locations_of_HTML_results here to keep from getting 'stale' and keeping the for loop the right length
        locations_of_HTML_results = driver.find_elements_by_xpath("//tr[@class='SearchResults']")
        for row in range(0, len(locations_of_HTML_results)):
            # Get single result
            row_element = locations_of_HTML_results[row]

            # Refresh original result
            row_element = locations_of_HTML_results[row]
            # Get details of original result from the search page
            data_elements = row_element.find_elements_by_xpath(".//td//div")

            parsed_results.append({})

            parsed_results[row]["Parcel ID"] = data_elements[1].text
            parsed_results[row]["Owner"] = data_elements[2].text
            parsed_results[row]["Parcel Address"] = data_elements[3].text
            parsed_results[row]["City"] = data_elements[4].text

            if (detailed == True):
                logwrite(f"Getting detailed data on property with Parcel ID {parsed_results[row]['Parcel ID']}")
                locations_of_HTML_results = get_detailed_data_on_search_result(row_element)

            if (detailed == False):
                write_basic_info(parsed_results[row])
        if detailed == -1:
            break
        if (click_next() == 0):
            break

    return parsed_results


def get_detailed_data_on_search_result(search_result_HTML_element):
    # actionChainsDriver.move_to_element(search_result_HTML_element).perform()
    # Click on search result
    search_result_HTML_element.click()
    # Wait to load
    content_panel__element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'contentpanel')))
    # Gather data
    list_of_data_attributes__elements = driver.find_elements_by_xpath("//td[@class='DataletSideHeading']")
    list_of_data_values__elements = driver.find_elements_by_xpath(
        "//td[@class='DataletSideHeading']/following-sibling::td[@class='DataletData']")
    profile_dict = dict()
    for i in range(0, len(list_of_data_values__elements)):
        # print(f"{list_of_data_attributes__elements[i].text}:\t{list_of_data_values__elements[i].text}")
        profile_dict[list_of_data_attributes__elements[i].text.strip(':')] = list_of_data_values__elements[i].text
    # print("\n")
    profilewrite(profile_dict)

    parcel_ID = profile_dict['Parcel ID']
    if profile_dict["Property Class"][0] == "R":
        get_sales_data_from_detailed_page(parcel_ID, maximum_number_of_sales_data=1)
        get_residential_data_from_detailed_page(parcel_ID)
    return move_back_from_details_to_search_results_with_nonstale_elements()


def get_sales_data_from_detailed_page(parcel_ID, maximum_number_of_sales_data=999):
    # Go to sales
    link_to_sales__element = driver.find_element_by_partial_link_text("Sales")
    link_to_sales__element.click()

    # Gather data from pages
    number_of_sales_collected = 0
    while (True):
        list_of_data_attributes__elements = driver.find_elements_by_xpath("//td[@class='DataletSideHeading']")
        list_of_data_values__elements = driver.find_elements_by_xpath(
            "//td[@class='DataletSideHeading']/following-sibling::td[@class='DataletData']")
        sales_dict = {'Parcel ID': parcel_ID}
        for i in range(0, len(list_of_data_values__elements)):
            # print(f"{list_of_data_attributes__elements[i].text}:\t{list_of_data_values__elements[i].text}")
            sales_dict[list_of_data_attributes__elements[i].text.strip(':')] = list_of_data_values__elements[i].text
        # print("\n")
        saleswrite(sales_dict)
        number_of_sales_collected += 1
        if number_of_sales_collected >= maximum_number_of_sales_data:
            # print("\n\n")
            return
        try:
            # Click on ">" button to move to next sale
            next_button__element = driver.find_element_by_class_name("icon-angle-right")
            next_button__element.click()
        except selenium.common.exceptions.NoSuchElementException:
            # print("\n\n")
            return


def get_residential_data_from_detailed_page(parcel_ID):
    # Go to residential page
    link_to_residential__element = driver.find_element_by_partial_link_text("Residential")
    link_to_residential__element.click()

    # Gather data from residential page
    list_of_data_attributes__elements = driver.find_elements_by_xpath("//td[@class='DataletSideHeading']")
    list_of_data_values__elements = driver.find_elements_by_xpath(
        "//td[@class='DataletSideHeading']/following-sibling::td[@class='DataletData']")
    residential_dict = {'Parcel ID': parcel_ID}
    for i in range(0, len(list_of_data_values__elements)):
        # print(f"{list_of_data_attributes__elements[i].text}:\t{list_of_data_values__elements[i].text}")
        residential_dict[list_of_data_attributes__elements[i].text.strip(':')] = list_of_data_values__elements[i].text
    # print("\n")
    residential_write(residential_dict)
    return


def move_back_from_details_to_search_results_with_nonstale_elements():
    link_to_search_results__element = driver.find_element_by_partial_link_text("Return to Search Results")
    link_to_search_results__element.click()

    #while (driver.current_url != "https://iaspublicaccess.fultoncountyga.gov/search/CommonSearch.aspx?mode=PARID"):
    #    driver.back()
    # Refresh search results so that we don't get "Stale Elements" error
    locations_of_HTML_results = driver.find_elements_by_xpath("//tr[@class='SearchResults']")
    # return the refreshed results
    return locations_of_HTML_results


def click_next():
    try:
        nextpage_element = driver.find_element_by_partial_link_text('Next >>')
        nextpage_element.click()
        sleep(0.5)
        found_nextpage = 1
    except:
        found_nextpage = 0
    return found_nextpage


def logwrite(logtext):
    with open('property_webscrape_log.txt', 'a') as logfile:
        logfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\t' + logtext + '\n')
        print(logtext)

    if "Completed collecting information for the search term" in logtext:
        search_term = logtext[53:]
        with open('property_webscrape_most_recent_search_term.txt', 'w') as most_recent_search:
            most_recent_search.write(search_term)
    return


def write_basic_info(dictin):
    with open('property_webscrape_parcel_basics.txt', 'a') as bfile:
        bfile.write(str(dictin) + '\n')
    return


def profilewrite(dictin):
    with open('property_webscrape_profile.txt', 'a') as pfile:
        pfile.write(str(dictin) + '\n')
    return


def saleswrite(dictin):
    with open('property_webscrape_sales.txt', 'a') as sfile:
        sfile.write(str(dictin) + '\n')
    return


def residential_write(dictin):
    with open('property_webscrape_residential.txt', 'a') as rfile:
        rfile.write(str(dictin) + '\n')
    return


def collect_ascending_descending(parcel_id_search_term):
    # Need to collect all the information ascending first
    parsed_results = collect_search_results_on_page(willDoADetailedSearch)
    # Then need to sort descending and search again
    selSortDir_input_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'selSortDir')))
    selSortDir_input_element.click()
    selSortDir_input_element.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    execute_search_query(parcel_id_search_term)
    # Need to collect all the information again
    parsed_results = collect_search_results_on_page(willDoADetailedSearch)
    sleep(1)
    # Need to sort ascending so that the next search isn't messed up
    selSortDir_input_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'selSortDir')))
    selSortDir_input_element.click()
    selSortDir_input_element.send_keys(Keys.ARROW_UP, Keys.ENTER)
    sleep(1)
    L_results = int(find_number_of_search_results())
    if (L_results >= 500):
        logwrite('Only able to collect 500 records of the ' + str(L_results) + ' records present')
    else:
        logwrite('Collected the ' + str(L_results) + ' records but duplicates will need to be removed')
    return


def find_search_terms_and_start_webscraping():
    # This defines the starting point of the searches
    try:
        parcel_id_container_file = open('property_webscrape_most_recent_search_term.txt', 'r')
        parcel_id_search_term = parcel_id_container_file.read()
        parcel_id_container_file.close()
        if len(parcel_id_search_term) == 0:
            parcel_id_search_term = '0'
    except FileNotFoundError:
        parcel_id_search_term = '0'

    dont_skip = 1  # This term makes it possible to deal with multiple levels of increments from 9s
    while (1):
        if (dont_skip):
            while (too_many_results() == 1):
                # Check to see if the next character is a space, if so then add two more characters
                if (parsed_results[0]['Parcel ID'][len(parcel_id_search_term)] == ' '):
                    if (parsed_results[0]['Parcel ID'][len(parcel_id_search_term) + 1] == 'L'):
                        # We are unable to narrow the search any further, so instead collect everything sorted ascending then descending
                        collect_ascending_descending(parcel_id_search_term)
                        break  # Exit the while loop, we have collected everything we can from h
                    else:
                        parcel_id_search_term = parsed_results[0]['Parcel ID'][0:len(parcel_id_search_term) + 2]
                else:
                    parcel_id_search_term = parsed_results[0]['Parcel ID'][0:len(parcel_id_search_term) + 1]
                logwrite('Parcel ID search term is now: ' + parcel_id_search_term)
                # print('Parcel ID search term is now: ' + parcel_id_search_term)
                execute_search_query(parcel_id_search_term)
                parsed_results = collect_search_results_on_page(-1)  # This collects the first parcel ID which is required, but does not get everything
            if (too_many_results() == 0):
                parsed_results = collect_search_results_on_page(willDoADetailedSearch)  # This collects everything
                logwrite('Completed collecting information for the search term ' + parcel_id_search_term)
        if (int(parcel_id_search_term[-1]) < 9):
            # increment the search term
            parcel_id_search_term = parcel_id_search_term[0:len(parcel_id_search_term) - 1] + str(
                int(parcel_id_search_term[-1]) + 1)
            logwrite('Parcel ID search term is now: ' + parcel_id_search_term)
            # print('Parcel ID search term is now: ' + parcel_id_search_term)
            execute_search_query(parcel_id_search_term)
            if (too_many_results() == -1):
                dont_skip = 0
            else:
                parsed_results = collect_search_results_on_page(-1)
                dont_skip = 1
        else:
            # The search term has reached the limit at this level, need to back out by one and increment
            # Don't want to increment it here, or we will have to deal with a possible case of increment from 9999999...
            # Instead, back out one level and skip the search term, let it loop around back to here
            if (len(parcel_id_search_term) == 4):
                # This deals with the space
                parcel_id_search_term = parcel_id_search_term[0:2]
            else:
                parcel_id_search_term = parcel_id_search_term[0:len(parcel_id_search_term) - 1]
            dont_skip = 0


if __name__ == "__main__":
    initiate_browser()

    #find_search_terms_and_start_webscraping()

    while(True):
        try:
            find_search_terms_and_start_webscraping()
        except selenium.common.exceptions.TimeoutException:
            logwrite("Experienced timeout exception. Waiting 3 minutes")
            sleep(60*3)
            initiate_browser()
        except selenium.common.exceptions.WebDriverException:
            logwrite("Experienced major exception, possible refusal of connection. Waiting 10 minutes")
            sleep(60*10)
            initiate_browser()


