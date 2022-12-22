# -*- coding: utf-8 -*-
#!/usr/bin/env python
from dts import DTS
import shutil
import os
import re


class Model:
    model_file = ""
    dts = None
    yaml = ""
    lookups = []
    lu_max = 45

    def __init__(self, model_file, model_path):
        self.model_file = os.path.join(model_path, "eurofever.yaml")
        shutil.copy(model_file, self.model_file)
        self.yaml = ""
    
    def save(self):
        print("Save " + self.model_file)
        with open(self.model_file, "a") as f:
            f.write(self.yaml)
    
    def get_dts(self, file):
        self.dts = DTS(file)

    def set_lookup(self, name, description, sep, sep2):
        array = description.split(sep) 
        label = array[0].replace(sep2, "").strip()
        values = array[1].replace(sep2, "").replace("Values:", "").strip()
        if name == "lab_status":
            print(label)
            print(values)
        if name == "Ethnicity":
            values = re.sub("\(.*?\)", "", values)
        if name == "other" and "sign" in values and "musculoskeletal" in values:
            return ["YesNoUnknow", "Other (musculoskeletal sign)", [['1', 'Yes'], ['0', 'No'], ['99', 'Unknow']]]
        opts = []
        if ("," in values or ";" in values) and ("=" in values or ":" in values):
            opts = values.split("," if "," in values else ";")
            if len(opts) > 1:
                lookup = ""
                options = []
                for opt in opts:
                    key_value = opt.split(":" if ":" in values else "=")
                    if len(key_value) > 1:
                        val1 = key_value[0].strip().title().replace("knonwn", "known")
                        val2 = key_value[1].strip().title().replace("knonwn", "known")
                        key = val2 if val1.isnumeric() else val1
                        value = val1 if val1.isnumeric() else val2
                        options.append([value, key])
                        lookup += key.replace(" ", "").replace("-", "")
                if len(lookup) > self.lu_max:
                    lookup = lookup[0:self.lu_max]
                return [lookup, label, options]
        return [None, description, []]


    def check_lookup(self, name, description):
        lookup_table = None
        opts = []

        if name == "lab_status":
            [lookup_table, description, opts] = ["NotdoneDoneWaitingforresponse", "Lab exam status", [['0', 'Not done'], ['1', 'Done'], ['2', 'Waiting for response']]]
        elif name == "gender":
            [lookup_table, description, opts] = ["MaleFemale", "Gender", [['1', 'Male'], ['2', 'Female']]]
        elif name == "ConsanguSp":
            [lookup_table, description, opts] = ["Degrees", "Level of consanguinity", [['1', 'First degree relative'], ['2', 'Second degree relative'], ['3', 'Third degree relative']]]
        elif "hpc" in str(description).lower():
            if "(muco cutaneous sign)" in description:
                description = "Other muco cutaneous sign"
            [lookup_table, description, opts] = ["NeverSometimesAlwaysNotknown", description.split("(")[0].strip(), [['0', 'Never'], ['1', 'Sometimes'], ['2', 'Always'], ['99', 'Not Known']]]
        elif (name.startswith("reason_") and "yes" in description) or name == "ever_taken":
            [lookup_table, description, opts] = ["YesNo", description.split(",")[0].strip(), [['1', 'Yes'], ['0', 'No']]]
        
        elif ";" in description and ":" in description and "," in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, ";", "")
        elif "(" in description and ")" in description and "[" not in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, "(", ")")
        elif "(" in description and ")" in description and "[" in description and "]" in description:
            [lookup_table, description, opts] = self.set_lookup(name, description, "[", "]")
        if lookup_table == "MusculoskeletalSign(YesNoUnknow":
            [lookup_table, description, opts] = ["YesNoUnknow", "Other Musculoskeletal Sign", [['1', 'Yes'], ['0', 'No'], ['99', 'Unknow']]]
        return [lookup_table, description.replace(":", ""), opts]
    
    def get_yaml(self):
        self.yaml += self.dts.set_header()
        names = []
        if self.dts.group != "patients":
            self.yaml += self.dts.set_attr("auto_id", "Autoincremental ID", "string", None, True, self.dts.group)
            names.append("auto_id")
        for index, row in self.dts.df.iterrows():
            name = row["field_name"]
            if "Gaslini" in name:
                if "min" in name:
                    name = "gaslini_lab_min"
                elif "max" in name:
                    name = "gaslini_lab_max"
                else:
                    name = "gaslini_stand_value"
            if "table_name" in self.dts.df.columns:
                name = row["table_name"] + "_" + row["field_name"]
            if name in names:
                print("Field " + name + " already inserted")
                continue
            names.append(name)
            description = str(row["field_description"])
            dataType = row["DATA_TYPE"]
            [lookup_table, description, opts] = self.check_lookup(name, description)
            #if lookup_table is not None:
            #    print(description)
            #    print(lookup_table)
            #    print(opts)
            #    print("\n")
            if lookup_table is not None and any(lookup_table == lu[0] for lu in self.lookups) == False:
                self.lookups.append([lookup_table, opts])
            isKey = name == "export_id_pt" and self.dts.group == "patients"
            self.yaml += self.dts.set_attr(name, description, dataType, lookup_table, isKey, self.dts.group)
