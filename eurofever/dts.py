# -*- coding: utf-8 -*-
#!/usr/bin/env python
from pandas import read_excel


class DTS:
    df = None
    group = ""

    def __init__(self, excel):
        self.df = read_excel(excel, sheet_name=0, header=0, dtype=str)
        self.df = self.df[~self.df.field_name.isin(["Project_Name"])]
    

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
        if str(name).endswith("export_id_pt") and group != "patients":
            yaml += "        dataType: xref\n"
            yaml += "        refEntity: efm_patients\n"
        elif lookup_table is not None:
            yaml += "        dataType: xref\n"
            yaml += "        refEntity: efm_lookups_" + lookup_table + "\n"
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
        yaml += "  # @name efm_" + name + "\n"
        yaml += "  - name: " + name + "\n"
        yaml += "    label: " + label + "\n"
        yaml += "    description: Eurofever " + self.group + " data\n"
        yaml += "    attributes:\n"
        return yaml
