# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import os
import csv

prefix = "psm"
study = "PerSAIDs"
file_entities = "./data_entities.tsv"
file_files = "./data_files.tsv"

DTSs = [
    "PATIENTS",
    "PT_INFO",
    "P_Proband",
    "DIAGNOSIS_AUTOINF",
    "CONCOMITANT",
    "LAB_EXAM",
    "MOLECULAR_ANALYSIS",
    "VISITS",
    "SGNS_SYMPTMS",
    "THERAPY_SUM",
    "THERAPY_HEIGHT_WIEGHT",
    "SAF_REPORT",
    "SAF_DRUGS",
    "SAF_TREAT_DRUGS",
    "SAF_REL_DRUGS",
    "SAF_ESI_FORM" #,
    #"SAF_PREGNANCY"
]

excluded_fields = [
    "id_lab",
    "classification",
    "Project_Name"
]

def get_entity(request: any, entity: str, value: str):
    res = None
    try:
        res = request.get("v1/psm_" + entity + "/" + value)
    except Exception as e: 
        print("Entity '" + entity + "' " + value + " not retrieved: " + str(e))
    return res


def save_entity(request: any, entity: str, id_value: str, data: any):
    res = "OK"
    try:
        if id_value == None:
            res = request.post("v1/psm_" + entity, 'application/json', data)
        else: 
            res = request.put("v1/psm_" + entity + "/" + id_value, 'application/json', data)
    except Exception as e: 
        print("Entity '" + entity + "' " + id_value + " not saved: " + str(e))
        return False
    return res != None

def set_value(value: any):
    value = str(value)
    return  None if value == 'nan' else value

def set_data(obj, fields):
    json_obj = {}
    for field in fields:
        value = getattr(obj, field)
        json_obj[field] = value
    return json.dumps(json_obj)

def set_date(value: any):
    value = str(value)
    if value == 'nan' or "-" not in value or ":" not in value:
        return None
    try: 
        value = value.replace(" 00:00:00", "")
    except Exception as e: 
        return None
    return value



def upload_file(request, file_full, file_name = ""):
    if file_name == "":
        file_name = os.path.basename(file_full)
    if os.path.exists(file_full) == False:
        print("File " + file_full + " does not exists!")
        return None
    
    data_files = []
    if os.path.exists(file_files) == False:
        os.mknod(file_files)
    with open(file_files) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            data_files.append(line)
    
    for f in data_files:
        if f[0] == file_name:
            print("File " + file_name + " is already uploaded as " + f[1])
            return f[1]
    
    res = request.post("files", 'application/json', open(file_full,'rb'), file_name)
    if res == None:
        print("File " + file_name + " cannot be uploaded!")
        return ""
    fileid = res.json()['id']
    with open(file_files, 'a') as tsvfile:
        tsvfile.write(file_name + "\t" + fileid + "\n")
    return fileid
        