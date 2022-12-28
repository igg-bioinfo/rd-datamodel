# -*- coding: utf-8 -*-
#!/usr/bin/env python
from pandas import read_excel
from math import nan


class DTS:
    df = None
    group = ""

    def __init__(self, excel):
        self.df = read_excel(excel, sheet_name=0, header=0, dtype=str)
        self.df = self.df[~self.df.field_name.isin(["Project_Name"])]

        #DTS - FIX DTS_P_Proband
        if "DTS_P_Proband" in excel:
            self.df = self.df[~self.df.field_name.isin(["export_id_pt"]) == False]
            self.add_row('PATIENT PROBAND', 'id_proband', 'Proband export ID')
            self.add_row('PATIENT PROBAND', 'rel_to_prob', 'Relation to proband')
            self.add_row('PATIENT PROBAND', 'dia_short', 'Diagnosis short name')
            print(self.df)

   
    def add_row(self, group, field, descr, type = 'string', min = nan, max = nan):
        new_row = {'export_group': group, 'field_name': field, 'field_description': descr, 'DATA_TYPE': type, 'limit_min': min, 'limit_max': max}
        self.df = self.df.append(new_row, ignore_index=True)


    def set_dataType(self, dataType):
        dataType = str(dataType).lower()
        if dataType == "string" or dataType == "nvarchar" or dataType == "varchar":
            dataType = "string"
        elif dataType == "float":
            dataType = "decimal"
        elif dataType == "bigint":
            dataType = "int"
        return dataType
    

    def set_attr(self, name, description, dataType, lookup_table, is_key, group):
        dataType = self.set_dataType(dataType)
        yaml = "\n"
        yaml += "      - name: " + name + "\n"
        if is_key:
            yaml += "        idAttribute: " + ("auto" if name == "auto_id" else "true") + "\n"
            yaml += "        nillable: false\n"
        if (str(name).endswith("export_id_pt") and group != "patients") or name == "id_proband":
            yaml += "        dataType: xref\n"
            yaml += "        refEntity: psm_patients\n"
        elif lookup_table is not None:
            yaml += "        dataType: xref\n"
            yaml += "        refEntity: psm_lookups_" + lookup_table + "\n"
        elif dataType is not None:
            yaml += "        dataType: " + dataType + "\n"
        yaml += "        description: " + description + "\n"
        return yaml
    

    def set_header(self):
        self.group = self.df["export_group"].iloc[0].lower()
        name = self.group.replace(" ", "_")
        label = self.group.title()
        yaml = "\n"
        yaml += "  #////////////////////////////////////////////////////////////////////////////\n"
        yaml += "  # @name psm_" + name + "\n"
        yaml += "  - name: " + name + "\n"
        yaml += "    label: " + label + "\n"
        yaml += "    description: PerSAIDs " + self.group + " data\n"
        yaml += "    attributes:\n"
        return yaml
