# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import csv
import pandas as pd
from utils import study, prefix, DTSs


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
    with open("./data_entities.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            data_entities.append(line)
    
    sh_txt = "# Import " + study + " datasets"
    sh_txt += "# <!--- start: listDatasetFiles --->"
    for dt in data_entities:
        sh_txt += "mcmd import " + dt[0].replace(".xlsx", "") + "\n"
        data_file = os.path.join(args.data_path, dt[0])
        if os.path.exists(data_file) == False:
            print("ERROR - " + data_file + " does not exist")
            return
        df = pd.read_excel(data_file, sheet_name=0, header=0)
        if 'Project_Name' in df.columns:
            df = df.drop('Project_Name', axis=1)
        with pd.ExcelWriter(data_file) as writer:
            df.to_excel(writer, sheet_name=dt[1], index=False)
        print("Save data " + data_file)
    sh_txt += "# <!--- end: listDatasetFiles --->"
    with open(os.path.join(args.data_path, "import_data_" + prefix + ".sh"), "w") as f:
        f.write(sh_txt)
    
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 create_import_data_files.py --data_path ./data