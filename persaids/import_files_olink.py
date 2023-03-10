# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import pandas as pd
from file import File
from request import Request
from utils import study, prefix, excluded_fields
import glob


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--olink_path', type=str, help='olink files path', required=True)
    return parser.parse_args(argv)

#MAIN THREAD
def main(argv):
    request = Request()
    args = get_args(argv)
    for file in glob.glob(os.path.join(args.olink_path, "*.csv")):
        oFile = File(file)
        oFile.update(request)

    
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 import_files_olink.py --olink_path ./files/olink