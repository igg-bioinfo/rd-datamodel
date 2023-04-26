# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
from classes.experiment_set import File
from classes.protocol import Protocol
from classes.request import Request
import glob


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--files_path', type=str, help='files path', required=True)
    return parser.parse_args(argv)

#MAIN THREAD
def main(argv):
    request = Request()
    args = get_args(argv)
    for pt_path in glob.glob(os.path.join(args.files_path, "pt_*/")): 
        pt_id = pt_path.replace("pt_", "").split("/")[2]
        oProtocol = Protocol(request, pt_id) 
        pt_array = pt_id.split("_")
        oProtocol.name = pt_array[0]
        oProtocol.version = pt_array[1]
        oProtocol.save(request)       
        for file in glob.glob(os.path.join(pt_path, "*.csv")):
            oFile = File(request, file)
            oFile.fileURI = "/api/files/" + oFile.file_id + "?alt=media"
            if oFile.metadata_id != None and oFile.metadata_id != "":
                oFile.metadataURI = "/api/files/" + oFile.metadata_id + "?alt=media"
            oFile.samplingProtocol = pt_id
            oFile.save(request)
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 7_FILES_IMPORT.py --files_path ./files