import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

start_year = int(input("Enter the start year (INCLUSIVE): "))
end_year = int(input("Enter the end year (INCLUSIVE): "))

driver = webdriver.Chrome(ChromeDriverManager().install())
url = "https://supremo.nic.in/KnowYourOfficerIAS.aspx"

# main page xpaths
YEAR_INPUT = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[1]/div/div/div[1]/div/div/input[1]"
SUBMIT_BUTTON = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[2]/input[1]"
RESET_BUTTON = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[2]/input[2]"

# front page xpaths
FRONT_TABLE = "/html/body/form/section[2]/div/div[1]/section/div/div/div[2]/div/div[4]/div[2]/table/tbody"

# profile page xpaths
MAIN_TABLE = "/html/body/form/div[3]/div[2]/div[1]/div/div/div[3]/table/tbody"
EDU_TABLE = "/html/body/form/div[3]/div[2]/div[1]/div/div/div[4]/div[1]/table[3]/tbody"
EXP_TABLE = "/html/body/form/div[3]/div[2]/div[1]/div/div/div[4]/div[1]/table[4]/tbody"

subject_to_cat = pd.read_csv("IAS subjects.csv")

def change_tab(num):
    handle = driver.window_handles[num]
    driver.switch_to.window(handle)

def close_current_tab():
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def clost_tab(num):
    handle = driver.window_handles[num]
    driver.switch_to.window(handle)
    driver.close()

def setQuery(year):
    # click the reset button
    driver.get(url)
    driver.find_element_by_xpath(RESET_BUTTON).click()

    # set the year
    year_input = driver.find_element_by_xpath(YEAR_INPUT)
    year_input.click()
    year_input.send_keys(str(year))

    # click the submit button
    driver.find_element_by_xpath(SUBMIT_BUTTON).click()

def reset_page():
    driver.get(url)

def openProfile(index):
    # get the table
    table = driver.find_element_by_xpath(FRONT_TABLE).find_elements_by_tag_name("tr")[1:][index]

    # get the first td
    td = table.find_elements_by_tag_name("td")[0]

    # click the link
    td.find_element_by_tag_name("a").click()

    # switch to the new tab
    change_tab(1)

def extract_main_table(trs, profile_data):
    # get the name
    name = trs[0].find_elements_by_tag_name("td")[0].text.strip()
    profile_data["Name"] = name

    # get the id value
    _id = trs[1].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["ID"] = _id if len(_id) <= 8 else _id[2:]
 
    row = trs[2].find_elements_by_tag_name("td")[1].text.strip().split("/")
    # service/cadre/allotment year set these in the profile data dictionary
    profile_data["Service"] = row[0].strip()
    profile_data["Cadre"] = row[1].strip()
    profile_data["Allotment_Year"] = row[2].strip()

    # extract from Source of recruitment to retirement reason, no need to split at /, and wait before you do retirement reason
    row = trs[3].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Source_of_Recruitment"] = row

    row = trs[4].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Date_of_Birth"] = row

    row = trs[5].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Gender"] = row

    row = trs[6].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Place_of_Domicile"] = row

    row = trs[7].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Mother_Tongue"] = row

    row = trs[8].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Languages_Known"] = row

    row = trs[9].find_elements_by_tag_name("td")[1].text.strip()
    profile_data["Retired"] = False if (row == "Serving" or row == "") else True
    profile_data["Retirement_Reason"] = row if row != "" else "Serving"

    return profile_data

def extract_edu_table(trs, template):
    education_data = []

    i=0
    while i < len(trs):
        temp = template
        tr = trs[i]
        tds = tr.find_elements_by_tag_name("td")[1:]

        temp["Reference_Value"] = str(i)
        temp["Qualification"] = tds[0].text.split("\n")[0].strip()
        temp["Subject"] = tds[1].text.split("\n")[0].strip()
        temp["Division"] = tds[2].text.split("\n")[0].strip()
        education_data.append(temp.copy())
        i+=2
    
    return education_data

def extract_exp_table(trs, template):
    experience_data = []

    i=0
    while i < len(trs):
        temp = template
        tr = trs[i]
        tds = tr.find_elements_by_tag_name("td")[1:]

        temp["Reference_Value"] = str(i)
        temp["Designation"] = tds[0].text.split("\n")[0].strip()
        temp["Level"] = tds[0].text.split("\n")[1].strip()
        temp["Office"] = tds[1].text.split("\n")[0].strip()
        temp["Organisation"] = tds[2].text.strip()
        temp["Field_of_Experience"] = tds[3].text.split("/")[0].strip()
        temp["Category_of_Experience"] = tds[3].text.split("/")[1].strip()
        temp["Start_Date"] = tds[4].text.split("-")[0].strip()
        temp["End_Date"] = tds[4].text.split("-")[1].strip()


        experience_data.append(temp.copy())
        i+=1
    
    return experience_data

def extract_profile():
    change_tab(1)

    # profile data
    profile_data = {
        "ID": "",
        "Name":"",
        "Service":"",
        "Cadre":"",
        "Allotment_Year":"",
        "Date_of_Birth":"",
        "Date_of_Joining": "",
        "Source_of_Recruitment":"",
        "Gender":"",
        "Place_of_Domicile": "",
        "Mother_Tongue":"",
        "Languages_Known":"",
        "Retired" : "",
        "Retirement_Reason" : "",
        "Source" : "Supremo",
        "Last_Education_Qualification":"",
        "Last_Education_Subject": "",
        "Last_Education_Division":"",
        "Last_Designation":"",
        "Last_Level": "",
        "Last_Office": "",
        "Last_Field_of_Experience": "",
        "Last_Category_of_Experience": "",
        "Last_Start_Date": "",
        "Last_End_Date": "",
    }

    # extract the main table
    trs = driver.find_element_by_xpath(MAIN_TABLE).find_elements_by_tag_name("tr")
    profile_data = extract_main_table(trs, profile_data)

    education_data = {
        "ID": profile_data["ID"],
        "Name":profile_data["Name"],
        "Service":profile_data["Service"],
        "Cadre":profile_data["Cadre"],
        "Reference_Value":"0",
        "Qualification":"N.A.",
        "Subject":"N.A.",
        "Division":"N.A.",
        "Source":"Supremo",
    }

    experience_data = {
        "ID": profile_data["ID"],
        "Name":profile_data["Name"],
        "Service":profile_data["Service"],
        "Cadre":profile_data["Cadre"],
        "Reference_Value":"",
        "Designation":"",
        "Level":"",
        "Office":"",
        "Organisation":"",
        "Field_of_Experience":"",
        "Category_of_Experience":"",
        "Start_Date":"",
        "End_Date":"",
        "Source":"Supremo",
    }

    

    try:
        trs = driver.find_element_by_xpath(EDU_TABLE).find_elements_by_tag_name("tr")
        education_data = extract_edu_table(trs, education_data)

        last_education = education_data[-1]
        profile_data["Last_Education_Qualification"] = last_education["Qualification"]
        profile_data["Last_Education_Subject"] = last_education["Subject"]
        profile_data["Last_Education_Division"] = last_education["Division"]
    except:
        pass
    
    try:
        trs = driver.find_element_by_xpath(EXP_TABLE).find_elements_by_tag_name("tr")
        experience_data = extract_exp_table(trs, experience_data)

        last_experience = experience_data[0]
        profile_data["Last_Designation"] = last_experience["Designation"]
        profile_data["Last_Level"] = last_experience["Level"]
        profile_data["Last_Office"] = last_experience["Office"]
        profile_data["Last_Field_of_Experience"] = last_experience["Field_of_Experience"]
        profile_data["Last_Category_of_Experience"] = last_experience["Category_of_Experience"]
        profile_data["Last_Start_Date"] = last_experience["Start_Date"]
        profile_data["Last_End_Date"] = last_experience["End_Date"]
    except:
        pass

    close_current_tab()
    
    return profile_data, education_data, experience_data

profile_df = pd.DataFrame()
education_df = pd.DataFrame()
experience_df = pd.DataFrame()

for year in range(start_year, end_year+1):
    print(year)
    reset_page()
    setQuery(year)

    main_table = driver.find_element_by_xpath(FRONT_TABLE).find_elements_by_tag_name("tr")[1:]

    for row in tqdm(main_table):
        # get the tds of the row
        tds = row.find_elements_by_tag_name("td")
        date_of_joining = tds[-1].text.split("\n")[0].strip()

        # click in the first td
        tds[0].find_element_by_tag_name("a").click()

        profile_data, education_data, experience_data = extract_profile()

        profile_data["Date_of_Joining"] = date_of_joining

        profile_df = profile_df.append(profile_data, ignore_index=True)
        education_df = education_df.append(education_data, ignore_index=True)
        experience_df = experience_df.append(experience_data, ignore_index=True)

driver.close()

# save to csv in 'rescrapped' folder
profile_df.to_csv(f"rescrapped/profile_{start_year}-{end_year}.csv", index=False)
education_df.to_csv(f"rescrapped/education_{start_year}-{end_year}.csv", index=False)
experience_df.to_csv(f"rescrapped/experience_{start_year}-{end_year}.csv", index=False)