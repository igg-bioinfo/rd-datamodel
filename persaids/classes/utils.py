# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json

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
    try:
        if id_value == None:
            request.post("v1/psm_" + entity, 'application/json', data)
        else: 
            request.put("v1/psm_" + entity + "/" + id_value, 'application/json', data)
    except Exception as e: 
        print("Entity '" + entity + "' " + id_value + " not saved: " + str(e))

def set_value(value: any):
    value = str(value)
    return  None if value == 'nan' else value

def set_data(obj, fields):
    json_obj = {}
    for field in fields:
        value = getattr(obj, field)
        json_obj[field] = value
    return json.dumps(json_obj)
        