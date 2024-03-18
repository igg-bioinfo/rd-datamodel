# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import csv
import pandas as pd
from classes.utils import study, prefix, excluded_fields, file_entities


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, help='data path', required=True)
    return parser.parse_args(argv)


#MAIN THREAD
def main(argv):
    args = get_args(argv)

    #GET DATA FILES & ENTITIES
    data_entities = []
    with open(file_entities) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            data_entities.append(line)
    
    sh_txt = "# Import " + study + " datasets\n"
    sh_txt += "# <!--- start: listDatasetFiles --->\n"
    for dt in data_entities:
        data_file = os.path.join(args.data_path, dt[0])
        sh_txt += "mcmd import --from-path " + data_file + "\n"
        if os.path.exists(data_file) == False:
            print("ERROR - " + data_file + " does not exist")
            return
        df = pd.read_excel(data_file, sheet_name=0, header=0)
        for excluded_field in excluded_fields:
            if excluded_field in df.columns:
                df = df.drop(excluded_field, axis=1)
        with pd.ExcelWriter(data_file) as writer:
            df.to_excel(writer, sheet_name=dt[1].replace('psm_', ''), index=False)
        print("Save data " + data_file)
    sh_txt += "# <!--- end: listDatasetFiles --->\n"
    with open("5_EF_IMPORT.sh", "w") as f:
        f.write(sh_txt)
    
    one_file = os.path.join(args.data_path, 'ALL_DATA.xlsx')
    with pd.ExcelWriter(one_file) as one_writer:
        for dt in data_entities:
            data_file = os.path.join(args.data_path, dt[0])
            if os.path.exists(data_file) == False:
                print("ERROR - " + data_file + " does not exist")
                return
            df = pd.read_excel(data_file, sheet_name=0, header=0)
            for excluded_field in excluded_fields:
                if excluded_field in df.columns:
                    df = df.drop(excluded_field, axis=1)
            df.to_excel(one_writer, sheet_name=str(dt[1]).replace('psm_', ''), index=False)
    
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 4_EF_IMPORT_FILES.py --data_path ./data