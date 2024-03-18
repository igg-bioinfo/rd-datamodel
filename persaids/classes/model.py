# -*- coding: utf-8 -*-
#!/usr/bin/env python
from classes.dts import DTS
import shutil
import os
import re
import csv
from classes.utils import prefix, file_entities


class Model:
    model_file = ""
    dts = None
    yaml = ""
    lookups = []
    lu_max = 30
    data_entities = []


    def __init__(self, model_file, model_path):
        self.model_file = os.path.join(model_path, prefix + ".yaml")
        shutil.copy(model_file, self.model_file)
        self.yaml = ""
        self.lookups = []
        self.data_entities = []
    

    def save(self):
        print("Save " + self.model_file)
        fin = open(self.model_file, "rt")
        data = fin.read()
        data = data.replace('#EF_TABLES#', self.yaml)
        fin.close()
        fin = open(self.model_file, "wt")
        fin.write(data)
        fin.close()
        #with open(self.model_file, "a") as f:
        #    f.write(self.yaml)
        with open(file_entities, 'w', newline='') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
            writer.writerows(self.data_entities)
    

    def get_dts(self, file):
        self.dts = DTS(file)

    
    def norm_value(self, value):
        value = value.strip().title()
        value = value.replace("knonwn", "known")
        value = value.replace("&Gt;", "Greater than ")
        value = value.replace("&Lt;", "Less than ")
        value = value.replace("  ", " ")
        if value.endswith("know"):
            value += "n"
        return value


    def set_lookup(self, name, description, sep, sep2):
        array = description.split(sep) 
        label = array[0].replace(sep2, "").strip()
        values = array[1].replace(sep2, "").replace("Values:", "").strip()
            
        #LOOKUP - FIX BY OPTIONS
        if name == "Ethnicity":
            values = re.sub("\(.*?\)", "", values)
        if name == "other" and "sign" in values and "musculoskeletal" in values:
            return ["YesNoUnknown", "Other (musculoskeletal sign)", [['1', 'Yes'], ['0', 'No'], ['99', 'Unknown']]]
            
        #LOOKUP - GET OPTIONS
        opts = []
        if ("," in values or ";" in values) and ("=" in values or ":" in values):
            opts = values.split("," if "," in values else ";")
            if len(opts) > 1:
                lookup = ""
                options = []
                for opt in opts:
                    key_value = opt.split(":" if ":" in values else "=")
                    if len(key_value) > 1:
                        val1 = self.norm_value(key_value[0])
                        val2 = self.norm_value(key_value[1])
                        key = val2 if val1.isnumeric() else val1
                        value = val1 if val1.isnumeric() else val2
                        options.append([value, key])
                        lookup += key.replace(" ", "").replace("-", "")
                if len(lookup) > self.lu_max:
                    lookup = lookup[0:self.lu_max]
                if lookup[0].isnumeric():
                    lookup = 'N' + lookup[1:self.lu_max]

                return [lookup, label, options]
        return [None, description, []]


    def check_lookup(self, name, description):
        lookup_table = None
        opts = []

        #LOOKUP - FIX BY NAME
        if name == "Intensit":
            [lookup_table, description, opts] = ["VerySevereSevereModerateNone", "Intensity", [['0', 'None'], ['1', 'Very Severe'], ['2', 'Severe'], ['3', 'Moderate'], ['4', 'Mild']]]
        elif name == "lab_status":
            [lookup_table, description, opts] = ["NotdoneDoneWaitingforresponse", "Lab exam status", [['0', 'Not done'], ['1', 'Done'], ['2', 'Waiting for response']]]
        elif name == "gender":
            [lookup_table, description, opts] = ["MaleFemale", "Gender", [['1', 'Male'], ['2', 'Female']]]
        elif name == "ConsanguSp":
            [lookup_table, description, opts] = ["Degrees", "Level of consanguinity", [['1', 'First degree relative'], ['2', 'Second degree relative'], 
            ['3', 'Third degree relative'], ['4', 'Fourth degree relative'], ['5', 'Fifth degree relative'], ['6', 'Sixth degree relative']]]
        elif "hpc" in str(description).lower():
            if "(muco cutaneous sign)" in description:
                description = "Other muco cutaneous sign"
            [lookup_table, description, opts] = ["NeverSometimesAlwaysNotKnown", description.split("(")[0].strip(), [['0', 'Never'], ['1', 'Sometimes'], ['2', 'Always'], ['99', 'Not Known']]]
        elif (name.startswith("reason_") and "yes" in description) or name == "ever_taken":
            [lookup_table, description, opts] = ["YesNo", description.split(",")[0].strip(), [['1', 'Yes'], ['0', 'No']]]
            
        #LOOKUP - FIX BY SEPARATOR
        elif ";" in description and ":" in description and "," in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, ";", "")
        elif "(" in description and ")" in description and "[" not in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, "(", ")")
        elif "(" in description and ")" in description and "[" in description and "]" in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, "[", "]")
            
        #LOOKUP - FIX BY LOOKUP
        if lookup_table == "MusculoskeletalSign(YesNoUnknown":
            [lookup_table, description, opts] = ["YesNoUnknown", "Other Musculoskeletal Sign", [['1', 'Yes'], ['0', 'No'], ['99', 'Unknown']]]
        
        return [lookup_table, description.replace(":", ""), opts]
    

    def get_yaml(self):
        self.yaml += self.dts.set_header()
        self.data_entities.append([self.dts.filename.replace("DTS_", "DT_"), prefix + "_" + self.dts.entity])
        names = []
        if self.dts.entity not in ["patients", "saf_report"]:
            self.yaml += self.dts.set_attr("auto_id", "Autoincremental ID", "string", None, True, self.dts.entity, False)
            names.append("auto_id")
        for index, row in self.dts.df.iterrows():
            field = row["field_name"]
            
            #FIELD - FIX GASLINI IN LAB EXAM
            if "Gaslini" in field:
                if "min" in field:
                    field = "gaslini_lab_min"
                elif "max" in field:
                    field = "gaslini_lab_max"
                else:
                    field = "gaslini_stand_value"
            
            #FIELD - FIX DUPLICATED FOR SIGNS & SYMPTOMS
            if "table_name" in self.dts.df.columns:
                field = row["table_name"] + "_" + row["field_name"]
            
            #FIELD - AVOID DUPLICATED
            if field in names:
                print("Field " + field + " already inserted")
                continue
            names.append(field)

            #FIELD - ADD
            description = str(row["field_description"])
            dataType = row["DATA_TYPE"]
            [lookup_table, description, opts] = self.check_lookup(field, description)
            if lookup_table == 'MusculoskeletalSign(YesNoUnkno':
                lookup_table = 'MusculoskeletalSignYesNoUnkno'
            isKey = (field == "patient_id" and self.dts.entity == "patients") or (field == "id_ae" and self.dts.entity == "saf_report")
            self.yaml += self.dts.set_attr(field, description, dataType, lookup_table, isKey, self.dts.entity)
            #if lookup_table == "a":
            #    print(description)
            #    print(lookup_table)
            #    print(opts)
            #    print("\n")
            
            #LOOKUP - AVOID DUPLICATED
            if lookup_table is not None and any(lookup_table == lu[0] for lu in self.lookups) == False:
                self.lookups.append([lookup_table, opts])
