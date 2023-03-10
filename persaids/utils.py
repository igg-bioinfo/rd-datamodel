# -*- coding: utf-8 -*-
#!/usr/bin/env python

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