# -*- coding: utf-8 -*-
#!/usr/bin/env python
import shutil
import os
import glob
from classes.utils import prefix, study


class Lookup:
    lookup_file = ""
    lookup_path = ""
    setup_file = ""
    template = "attributeTemplate" + study

    def __init__(self, lookup_file, setup_path, model_path, lookup_path):
        self.lookup_path = lookup_path
        self.lookup_file = os.path.join(model_path, prefix + "_lookups.yaml")
        shutil.copy(lookup_file, self.lookup_file)

        setup_file = os.path.join(setup_path, "setup.sh")
        self.setup_file = "3_MODEL_IMPORT.sh" #os.path.join(setup_path, "setup_" + prefix + ".sh")
        shutil.copy(setup_file, self.setup_file)

        for f in glob.glob(os.path.join(model_path, prefix + "_lookups_*.csv")):
            os.remove(f)


    def save_setup(self, text):
        print("Save " + self.setup_file)
        sof = "# <!--- start: listEmxFiles --->\n"
        
        file = open(self.setup_file, mode='r')
        text_base = file.read()
        file.close()
        text_final = text_base.replace("2021-11-10", "2022-12-01")
        text_final = text_final.replace("2022-02-02", "2022-12-01")
        text_final = text_final.split(sof)[0] + sof 
        text_final += "mcmd delete -p " + prefix + " # completing remove package\n"
        text_final += "mcmd import -p ../dist/" + study + ".xlsx\n"
        text_final += text
        text_final += "# <!--- end: listEmxFiles --->\n"
        with open(self.setup_file, "w") as f:
            f.write(text_final)

    def save_csv(self, name, options):
        file_name = prefix + "_lookups_" + name + ".csv"
        print("Save " + file_name)
        text = "value,description\n"
        for opt in options:
            text += opt[0] + "," + opt[1] + "\n"
        with open(os.path.join(self.lookup_path, file_name), "w") as f:
            f.write(text)

    def copy_lookups(self, lookups):
        file = open(self.lookup_file, mode='r')
        text = file.read()
        file.close()
        attr_occurences = text.split("    attributes:")
        text = attr_occurences[len(attr_occurences) - 1]
        for line in text.split("\n"):
            if line.startswith("  - name: "):
                lu_name = line.replace("  - name: ", "")
                file_name = "umdm_lookups_" + lu_name + ".csv"
                file_path = os.path.join(self.lookup_path, file_name)
                if os.path.exists(file_path) == False:
                    print("ERROR - " + file_path + " does not exist")
                    continue
                print("Copy " + file_name)
                shutil.copy(os.path.join(self.lookup_path, file_name), os.path.join(self.lookup_path, prefix + "_lookups_" + lu_name + ".csv"))
                lookups.append([lu_name]) 
        return lookups
    
    def save(self, lookups):
        lookups = self.copy_lookups(lookups)

        txt_setup = ""
        txt_yaml = ""
        print("Save " + self.lookup_file)
        txt_yaml += self.add_template()
        for lu in lookups:
            txt_setup += "mcmd import -p ../lookups/" + prefix + "_lookups_" + lu[0] + ".csv\n"
            if len(lu) == 2:
                txt_yaml += self.add(lu[0], study + " lookup")
                self.save_csv(lu[0], lu[1])
        with open(self.lookup_file, "a") as f:
            f.write(txt_yaml)
        self.save_setup(txt_setup)

    def add(self, name, description):
        yaml = "\n"
        yaml += "  - name: " + name + "\n"
        yaml += "    description: " + description + "\n"
        yaml += "    extends: " + prefix + "_lookups_" + self.template + "\n"
        return yaml

    def add_template(self):
        yaml = "\n\n\n"
        yaml += "  # @name " + self.template + "\n"
        yaml += "  # @description attribute template for tables where `value` is the primary key and label is description\n"
        yaml += "  - name: " + self.template + "\n"
        yaml += "    abstract: true\n"
        yaml += "    description: attribute template where value is the primary key and label is description\n"
        yaml += "    tags: NCIT_C45677 http://purl.obolibrary.org/obo/NCIT_C45677\n"
        yaml += "    attributes:\n"
        yaml += "      - name: value\n"
        yaml += "        idAttribute: true\n"
        yaml += "        nillable: false\n"
        yaml += "        tags: NCIT_C49100 http://purl.obolibrary.org/obo/NCIT_C49100\n"
        yaml += "        description: The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute.\n"
        yaml += "        \n"
        yaml += "      - name: description\n"
        yaml += "        dataType: text\n"
        yaml += "        lookupAttribute: true\n"
        yaml += "        labelAttribute: true\n"
        yaml += "        tags: NCIT_C25365 http://purl.obolibrary.org/obo/NCIT_C25365\n"
        yaml += "        description: A written or verbal account, representation, statement, or explanation of something\n"
        return yaml