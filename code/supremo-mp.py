from multiprocessing import Process, Manager, freeze_support
from selenium import webdriver
import pandas as pd
import os
import time
import math

DROPDOWN_XPATH = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div/ul"
OPTIONS_XPATH = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div/div/ul"
YEAR_INPUT = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[1]/div/div/div[1]/div/div/input[1]"
SUBMIT_BUTTON = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[2]/input[1]"
RESET_BUTTON = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[2]/input[2]"
TABLE = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[4]/div[2]"
TABLE_PRIMARY = "/html/body/form/div[3]/div[2]/div/div/div/div[1]/table"
TABLE_SECONDARY = "/html/body/form/div[3]/div[2]/div/div/div/div[2]"
DATE_OF_JOINING_TABLE_ROW = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[4]/div[2]/table/tbody/tr"
DATE_OF_JOINING_TABLE_ELEMENT = "/td[6]"

def make_verbose(done, total, max_lines=100,start_with=""):
    num_lines = int((done/total)*max_lines)
    lines = "="*num_lines
    spaces = " "*(max_lines-num_lines)
    print(f"\r{start_with}  {lines}>{spaces}  {done}/{total}", end="", sep=" ", flush=True)


def set_search_query(year, driver):
    driver.find_element_by_xpath(RESET_BUTTON).click()
    driver.find_element_by_xpath(DROPDOWN_XPATH).click()
    length = len(driver.find_element_by_xpath(OPTIONS_XPATH).find_elements_by_tag_name("li"))
    driver.find_element_by_xpath(OPTIONS_XPATH).find_elements_by_tag_name("li")[1].click()
    for i in range(2,length-1):
        driver.find_element_by_xpath(DROPDOWN_XPATH).click()
        driver.find_element_by_xpath(OPTIONS_XPATH).find_elements_by_tag_name("li")[i].click()
    
    year_input = driver.find_element_by_xpath(YEAR_INPUT)
    year_input.click()
    year_input.send_keys(str(year))

    driver.find_element_by_xpath(SUBMIT_BUTTON).click()


def extract_info_from_profile(url, driver_profile):
    info = {
        "Name":"",
        "Service":"",
        "Cadre":"",
        "Allotment Year":"",
        "Date of Birth":"",
        "Identity No.":"",
        "Source of Recruitment":"",
        "Gender":"",
        "Place of Domicile": "",
        "Mother Tongue":"",
        "Languages Known":"",
        "Retirement Reason":"",
        "Qualification/University/Institute":"",
        "Subject":"",
        "Division":"",
        "Designation/Level":"",
        "Ministry/Department/Office/Location":"",
        "Organisation":"",
        "Experience(major/minor)":"",
        "Period(From/To)":""
    }
    driver_profile.get(url)
    table_primary = driver_profile.find_element_by_xpath(TABLE_PRIMARY).find_elements_by_tag_name("tr")
    tables_secondary = driver_profile.find_element_by_xpath(TABLE_SECONDARY).find_elements_by_tag_name("table")

    t_identification = {
        "III. Educational Qualifications.": ["Qualification/University/Institute", "Subject", "Division"],
        "IV. Experience Details": ["Designation/Level", "Ministry/Department/Office/Location", "Organisation", "Experience(major/minor)", "Period(From/To)"]
    }

    for row in table_primary:
        tds = row.find_elements_by_tag_name("td")
        labels = tds[0].text.replace(":","").strip().split("/ ")
        values = tds[1].text.strip().split("/ ")
        for label, value in zip(labels, values):
            info[label] += value

    for table in tables_secondary[1:3]:
        thead = table.find_element_by_tag_name("thead")
        table_name = thead.find_element_by_tag_name("tr").text
        keys_to_address = t_identification.get(table_name, 0)
        try:
            trs = table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
            for j, row in enumerate(trs):
                if j%2 == 0:
                    end_string = ""
                    if j < (len(trs)-2):
                        end_string += "|"
                    items = row.find_elements_by_tag_name("td")[1:]
                    for i, key in enumerate(keys_to_address):
                        information_to_add = items[i].text.replace("\n", "/")
                        info[key] += information_to_add + end_string
        except:
            trs = None
            for i, key in enumerate(keys_to_address):
                information_to_add = ""
                info[key] += information_to_add
    return info


def scrape_table(table, info, year):
    keys = [key for key in info.keys()]
    trs = table.find_elements_by_tag_name("tr")[1:]
    length = len(trs)

    profile_links = []

    for k, tr in enumerate(trs):
        prof_url = tr.find_element_by_tag_name("a").get_property("href")
        info.get("Profile URL", 0).append(prof_url)
        profile_links.append(prof_url)
        info.get("Date of Joining", 0).append(tr.find_element_by_xpath(f"/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[4]/div[2]/table/tbody/tr[{str(k+2)}]/td[6]").text)
        
        return profile_links


def job(profile_list, info, year, profile_driver, process_number, total_processes):
    target = process_number
    while target < len(profile_list):
        profile_url = profile_list[target]

        information = extract_info_from_profile(profile_url, profile_driver)

        for key in information.keys():
            info.get(key, 0).append(information[key])

        target += total_processes
        print(target)
        # make_verbose(target, len(profile_list), 25, year)


def cycle(year, main_driver, profile_drivers, num_processes, common_d):
    set_search_query(year, main_driver)
    table = main_driver.find_element_by_xpath(TABLE)
    profile_list = scrape_table(table, common_d, year)
    print(profile_list)
    processes = []
    for i in range(num_processes):
        process = Process(target=job, args=(profile_list, common_d, year, profile_drivers[i], i, num_processes,))
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()



if __name__ == '__main__':
    freeze_support()
    URL="https://supremo.nic.in/KnowYourOfficerIAS.aspx"
    DRIVER_PATH = 'C:/Users/vedan/Desktop/python-utils/chromedriver/chromedriver.exe'
    main_driver = webdriver.Chrome(DRIVER_PATH)
    main_driver.get(URL)
    num_processes = int(input("Number of processes?\n"))
    start_year = int(input("Start year?\n"))
    end_year = int(input("End year?\n"))
    profile_drivers = []
    keys = [
        "Name",
        "Service",
        "Cadre",
        "Allotment Year",
        "Date of Birth",
        "Date of Joining",
        "Identity No.",
        "Source of Recruitment",
        "Gender",
        "Place of Domicile",
        "Mother Tongue",
        "Languages Known",
        "Retirement Reason",
        "Qualification/University/Institute",
        "Subject",
        "Division",
        "Designation/Level",
        "Ministry/Department/Office/Location",
        "Organisation",
        "Experience(major/minor)",
        "Period(From/To)",
        "Profile URL"
    ]

    manager = Manager()
    common_d = manager.dict()
    for key in keys:
        common_d[key] = []

    for i in range(num_processes):
        profile_drivers.append(webdriver.Chrome(DRIVER_PATH))


    for year in range(start_year, end_year+1):
        cycle(year, main_driver, profile_drivers, num_processes, common_d)


    main_driver.close()
    for driver in profile_drivers:
        driver.close()