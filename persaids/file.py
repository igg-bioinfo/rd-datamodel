from request import Request
import json
import os
from datetime import date
from utils import file_files
import csv


class File:
    filename: str
    samples: list = []
    error: bool = False

    def __init__(self, filename):
        self.filename = filename
        filecfg = os.path.splitext(self.filename)[0] + ".cfg"
        if os.path.exists(self.filename) == False:
            print("File " + self.filename + " does not exist!")
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

    def check_samples(self, request):
        samples = []
        for sample in self.samples:
            res = request.get("v1/psm_samples/" + sample)
            if res != None and res.json()['sampleID']:
                samples.append(res.json()['sampleID'])
        self.samples = samples

    def check_file(self, request):
        if os.path.exists(file_files) == False:
            os.mknod(file_files)
        data_files = []
        with open(file_files) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            for line in tsv_file:
                data_files.append(line)

        file = os.path.basename(self.filename)
        
        for f in data_files:
            if f[0] == file:
                print("File " + file + " is already imported as " + f[1])
                return f[1]
        
        res = request.post("files", 'application/json', open(self.filename,'rb'), file)
        if res == None:
            return
        fileid = res.json()['id']
        with open(file_files, 'a') as tsvfile:
            tsvfile.write(file + "\t" + fileid)
        return fileid
        
        
        
        





    def update(self, request):
        if self.error:
            return
        file = os.path.basename(self.filename)
        try:
            self.check_samples(request)
            if (len(self.samples) == 0):
                print("File " + file + " has no sample to link!")
                return
            fileid = ""
            entityExist = request.get("v1/psm_files/" + file)
            if entityExist == None:
                fileid = self.check_file(request)
                data = json.dumps({
                    "fileID": file,
                    "belongsToSample": self.samples, 
                    "fileName": file,
                    "alternativeFileIdentifiers": fileid,
                    "dateRecordCreated": str(date.today()),
                    "recordCreatedBy": "system",
                    "URL": "/api/files/" + fileid + "?alt=media"

                })
                res = request.post("v1/psm_files", 'application/json', data)
            else: 
                fileid = entityExist.json()["alternativeFileIdentifiers"]
                data = json.dumps({
                    "fileID": file,
                    "belongsToSample": self.samples, 
                    "fileName": file,
                    "alternativeFileIdentifiers": fileid,
                    "dateRecordCreated": str(date.today()),
                    "recordCreatedBy": "system",
                    "URL": "/api/files/" + fileid + "?alt=media"
                })
                res = request.put("v1/psm_files/" + file, 'application/json', data)
        except Exception as e: 
            print("File " + file + " not updated: " + str(e))
    