import pandas as pd
import json
import os
from helper import Verbose
verbose = Verbose()

filename = input()

df = pd.read_csv(f"./outputs/combined/{filename}")

edu_df = pd.DataFrame(columns=["ID","Name","Service","Cadre","Qualification","Subject","Division","Source"])
exp_df = pd.DataFrame(columns=["ID","Name","Service","Cadre","Designation","Level","Office","Organisation","Major_Experience","Minor_Experience","Start_Date","End_Date","Source"])
edu_columns = ["Qualification/University/Institute","Subject","Division"]
exp_columns = ["Designation/Level","Ministry/Department/Office/Location","Organisation","Experience(major/minor)","Period(From/To)"]

def make_edu_row(row):
    columns = list(edu_df.columns)[4:7]
    template = {
        "ID" : row["Clean Ids"],
        "Name" : row["Name"],
        "Service" : row["Service"],
        "Cadre" : row["Cadre"]
    }
    edu_rows = []
    edu_length = len(row["Qualification/University/Institute"].split("|"))
    splits = [row[item].split("|") for item in edu_columns]
    for i in range(edu_length):
        template = {
            "ID" : row["Clean Ids"],
            "Name" : row["Name"],
            "Service" : row["Service"],
            "Cadre" : row["Cadre"]
        }
        for item, column in zip(splits, columns):
            template["Reference_Value"] = i
            template[column] = item[i]
        template["Source"] = row["Dataset name"]
        edu_rows.append(template)
    return edu_rows

def create_json_object(row):
    row_object = {}
    for key in row.keys():
        if key in list_columns:
            row_object[key] = row[key].split("|")
        else:
            row_object[key] = str(row[key]).strip()
    return row_object

def resructure_json(j_object):
    id_val = j_object["Clean Ids"]
    new_object = {}
    education_keys = ['Qualification/University/Institute', 'Subject', 'Division']
    experience_keys = ['Designation/Level', 'Ministry/Department/Office/Location', 'Organisation', 'Experience(major/minor)', 'Period(From/To)']
    for key in j_object.keys():
        if not (key in education_keys or key in experience_keys) and not key == "Clean Ids":
            new_object[key] = j_object[key]

    education_length = len(j_object["Subject"])
    edu_objects = []
    for i in range(education_length):
        edu_object = {}
        for key in education_keys:
            try:
                edu_object[key] = j_object[key][i]
            except:
                edu_object[key] = "N.A."
        
        edu_objects.append(edu_object)
    
    new_object["Education"] = edu_objects
    
    experience_length = len(j_object["Designation/Level"])
    exp_objects = []
    for i in range(experience_length):
        exp_object = {}
        for key in experience_keys:
            if key == "Experience(major/minor)":
                values = j_object[key][i].split("/")
                exp_object["Experience Major"] = values[0]
                try:
                    exp_object["Experience Minor"] = values[1]
                except:
                    exp_object["Experience Minor"] = "N.A."
            elif key == "Designation/Level":
                values = j_object[key][i].split("/")
                exp_object["Designation"] = values[0]
                try:
                    exp_object["Level"] = values[1]
                except:
                    exp_object["Level"] = "N.A."
            elif key == "Period(From/To)":
                values = j_object[key][i].split(" - ")
                exp_object["Period Start"] = values[0]
                try:
                    exp_object["Period End"] = values[1]
                except:
                    exp_object["Period End"] = "N.A."
            else:
                try:
                    exp_object[key] = j_object[key][i]
                except:
                    exp_object[key] = "N.A."
        
        exp_objects.append(exp_object)

    new_object["Experience"] = exp_objects
    return j_object["Clean Ids"], new_object