import json
import os
from classes.utils import file_files, save_entity, set_data, get_entity
from classes.sample import Sample
import csv


class File:
    exists: bool = False
    entity: str = "files"
    field_key: str = "fileID"
    fields: list = ["fileID", "samplingProtocol", "fileName", "filePath", "fileURI"]

    file_id: str
    file: str
    file_name: str
    samples: list = []
    error: bool = False

    def __init__(self, request, filename):
        self.file_name = filename
        self.file = os.path.basename(self.file_name)
        id = self.file
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
                            setattr(self, field, res["samplingProtocol"])
                    else:
                        setattr(self, field, None)
                else:
                    setattr(self, field, value)
            else: 
                setattr(self, field, None)
        setattr(self, self.field_key, id)
        setattr(self, "fileName", id)
        self.get_samples()
        self.file_id = self.upload_file(request)


    def get_samples(self):
        filecfg = os.path.splitext(self.file_name)[0] + ".samples"
        if os.path.exists(self.file_name) == False:
            print("File " + self.file_name + " does not exist!")
            self.error = True
            return
        if os.path.exists(filecfg) == False:
            print("File " + filecfg + " does not exist!")
            self.error = True
            return

        lines = []
        with open(filecfg, "r") as reader:
            lines = reader.readlines()
        
        for line in lines:
            line = line.strip()
            if line != "":
                self.samples.append(line)
        if len(self.samples) == 0:
            print("File " + filecfg + " has no samples to link!")
            self.error = True


    def upload_file(self, request):
        if os.path.exists(file_files) == False:
            os.mknod(file_files)

        data_files = []
        with open(file_files) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            for line in tsv_file:
                data_files.append(line)
        
        for f in data_files:
            if f[0] == self.file:
                print("File " + self.file + " is already uploaded as " + f[1])
                return f[1]
        
        res = request.post("files", 'application/json', open(self.file_name,'rb'), self.file)
        if res == None:
            print("File " + self.file + " cannot be uploaded!")
            return ""
        fileid = res.json()['id']
        with open(file_files, 'a') as tsvfile:
            tsvfile.write(self.file + "\t" + fileid + "\n")
        return fileid


    def save(self, request):
        if self.error:
            return
        try:
            if self.file_id != "":
                save_entity(request, self.entity, getattr(self, self.field_key) if self.exists else None, set_data(self, self.fields))
                sample_added = 0
                for sample_id in self.samples:
                    sample = Sample(request, sample_id)
                    if sample.exists:
                        sample_added += 1
                        if sample.add_file(getattr(self, self.field_key)):
                            sample.save(request)
                print("File " + self.file + " is related to " + str(sample_added) + " samples")
        except Exception as e: 
            print("File " + self.file + " not updated: " + str(e))
    