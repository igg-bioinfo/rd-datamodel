import os
from classes.utils import upload_file, save_entity, set_data, get_entity
from classes.sample import Sample
import glob


class ExperimentSet:
    exists: bool = False
    entity: str = "experimentSets"
    field_key: str = "fileID"
    fields: list = ["fileID", "samplingProtocol", "fileName", "filePath", "metadataURI", "fileURI",
                    "filePart1URI", "filePart2URI", "filePart3URI", "filePart4URI", "filePart5URI"]

    file_id: str
    file: str
    file_name: str
    metadata: str
    metadata_name: str
    samples_name: str
    samples: list = []
    error: bool = False

    def __init__(self, request, filename):
        self.file_name = filename
        self.metadata_name = filename.replace(".csv", ".metadata").replace(".gz.part00", ".metadata")
        self.samples_name = filename.replace(".csv", ".samples").replace(".gz.part00", ".samples")
        self.file = os.path.basename(self.file_name)
        self.metadata = os.path.basename(self.metadata_name)
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
        self.file_id = upload_file(request, self.file_name, self.file)
        self.metadata_id = upload_file(request, self.metadata_name, self.metadata)
        self.fileURI = "/api/files/" + self.file_id + "?alt=media"
        if self.metadata_id != None and self.metadata_id != "":
            self.metadataURI = "/api/files/" + self.metadata_id + "?alt=media"
        index = 1
        for part_file in glob.glob(self.file_name.replace(".part00", "") + ".part*"):
            if part_file.endswith(".part00"):
                continue
            part_id = upload_file(request, part_file)
            setattr(self, "filePart" + str(index) + "URI", part_id)
            index += 1


    def get_samples(self):
        filecfg = self.samples_name
        if os.path.exists(self.file_name) == False:
            print("File " + self.file_name + " does not exist!")
            self.error = True
            return
        if os.path.exists(filecfg) == False:
            print("File " + filecfg + " does not exist!")
            self.error = True
            return

        lines = []
        self.samples = []
        with open(filecfg, "r") as reader:
            lines = reader.readlines()
        
        for line in lines:
            line = line.strip()
            if line != "":
                self.samples.append(line)
        if len(self.samples) == 0:
            print("File " + filecfg + " has no samples to link to!")
            self.error = True


    def save(self, request):
        if self.error:
            return
        try:
            if self.file_id != "":
                res = save_entity(request, self.entity, getattr(self, self.field_key) if self.exists else None, set_data(self, self.fields))
                sample_added = 0
                for sample_id in self.samples:
                    sample = Sample(request, sample_id)
                    if sample.exists:
                        print(sample_id)
                        sample_added += 1
                        if sample.add_file(getattr(self, self.field_key)):
                            sample.save(request)
                print("File " + self.file + " is related to " + str(sample_added) + " samples")
        except Exception as e: 
            print("File " + self.file + " not updated: " + str(e))
    