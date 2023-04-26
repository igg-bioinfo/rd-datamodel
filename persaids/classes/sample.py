# -*- coding: utf-8 -*-
#!/usr/bin/env python
from classes.utils import save_entity, set_data, get_entity

class Sample:
    exists: bool = False
    entity: str = "samples"
    field_key: str = "sampleID"
    fields: list = ["sampleID", "localID", "institute", "belongsToPatient", "experimentSets", "samplingDate", "diseaseStatus", "treatedStatus"]


    def __init__(self, request, id):
        obj = get_entity(request, self.entity, id)
        obj = None if obj == None else obj.json()
        self.exists = obj != None
        for field in self.fields:
            if obj != None and field in obj:
                value = obj[field]
                if type(value) is dict:
                    field_value = get_entity(request, self.entity + "/" + id, field)
                    if field_value != None:
                        res = field_value.json()
                        if 'items' in res:
                            values = []
                            for item in res['items']:
                                array = str(item['href']).split("/")
                                values.append(array[len(array) - 1]) 
                            setattr(self, field, values)
                        else:
                            setattr(self, field, res["patient_id"])
                    else:
                        setattr(self, field, None)
                else:
                    setattr(self, field, value)
            else: 
                setattr(self, field, None)
        setattr(self, self.field_key, id)

    def add_file(self, file):
        found = False
        for f in self.experimentSets:
            if f == file:
                found = True
                break
        if found == False:
            self.experimentSets.append(file)
        return found == False

    def set_disease(self, value: any):
        value = str(value).lower().strip()
        self.diseaseStatus = "Not known"
        if value == "active":
            self.diseaseStatus = "Active"
        elif value == "inactive":
            self.diseaseStatus = "Inactive"

    def set_treated(self, value: any):
        value = str(value).lower().strip()
        self.treatedStatus = "Not known"
        if value == "treated":
            self.treatedStatus = "Treated"
        elif value == "untreated":
            self.treatedStatus = "Untreated"
    
    def save(self, request):
        return save_entity(request, self.entity, getattr(self, self.field_key) if self.exists else None, set_data(self, self.fields))