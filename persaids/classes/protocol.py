# -*- coding: utf-8 -*-
#!/usr/bin/env python
from classes.utils import save_entity, get_entity, set_data

class Protocol:
    exists: bool = False
    entity: str = "protocols"
    field_key: str = "id"
    fields: list = ["id", "name", "description", "version", "uri"]


    def __init__(self, request, id):
        obj = get_entity(request, self.entity, id)
        obj = None if obj == None else obj.json()
        self.exists = obj != None
        for field in self.fields:
            if obj != None and field in obj:
                value = obj[field]
                setattr(self, field, value)
            else: 
                setattr(self, field, None)
        setattr(self, self.field_key, id)
    
    def save(self, request):
        save_entity(request, self.entity, getattr(self, self.field_key) if self.exists else None, set_data(self, self.fields))