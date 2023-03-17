# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
from classes.file import File
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
    for protocol in glob.glob(os.path.join(args.files_path, "pt_*/")):         
        for file in glob.glob(os.path.join(protocol, "*.csv")):
            oFile = File(request, file)
            oFile.fileURI = "/api/files/" + oFile.file_id + "?alt=media"
            oFile.save(request)
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 7_SAMPLES_FILE_IMPORT.py --files_path ./files