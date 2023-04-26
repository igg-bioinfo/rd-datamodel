# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import os
from datetime import datetime

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
        