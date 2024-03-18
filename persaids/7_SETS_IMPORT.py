# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
from classes.experiment_set import ExperimentSet
from classes.protocol import Protocol
from classes.request import Request
from classes.utils import upload_file
import glob


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--files_path', type=str, help='files path', required=True)
    return parser.parse_args(argv)

#MAIN THREAD
def main(argv):
    request = Request()
    if request.token == "":
        return
    args = get_args(argv)
    for pt_path in glob.glob(os.path.join(args.files_path, "pt_*/")): 
        pt_id = pt_path.replace("pt_", "").split("/")[2]
        oProtocol = Protocol(request, pt_id) 
        pt_array = pt_id.split("_")
        oProtocol.name = pt_array[0]
        oProtocol.version = pt_array[1]
        docx_files = glob.glob(os.path.join(pt_path, "*.docx"))  
        if len(docx_files) != 1:
            print("Protocol " + oProtocol.name + " does not have docx file!")
            continue
        docx_id = upload_file(request, docx_files[0])
        oProtocol.uri = "/api/files/" + docx_id + "?alt=media"
        oProtocol.save(request)   
        #for file in glob.glob(os.path.join(pt_path, "*.csv")) + glob.glob(os.path.join(pt_path, "*.part00")):
        for file in glob.glob(os.path.join(pt_path, "*.csv")) + glob.glob(os.path.join(pt_path, "*.tsv")):
            oExperimentSet = ExperimentSet(request, file, oProtocol.name.lower())
            oExperimentSet.samplingProtocol = pt_id
            oExperimentSet.save(request)
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 7_FILES_IMPORT.py --files_path ./files