# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
from model import Model
from lookup import Lookup

DTSs = ["PATIENTS",
    "PT_INFO",
    "P_Proband",
    "DIAGNOSIS_AUTOINF",
    "CONCOMITANT",
    "LAB_EXAM",
    "MOLECULAR_ANALYSIS",
    "SGNS_SYMPTMS",
    "THERAPY_SUM",
    "THERAPY_HEIGHT_WIEGHT",]

#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dts_path', type=str, help='dts source path', required=True)
    parser.add_argument('--yaml_path', type=str, help='yaml destination path', required=True)
    return parser.parse_args(argv)


#MAIN THREAD
def main(argv):
    args = get_args(argv)
    model_path = os.path.join(args.yaml_path, "model")
    lookup_path = os.path.join(args.yaml_path, "lookups")
    args.yaml_path
    if os.path.exists(args.dts_path) == False or os.path.exists(model_path) == False or os.path.exists(lookup_path) == False:
        print("ERROR - Some main folder does not exist")
        return
    model_file = os.path.join(model_path, "persaids.yaml")
    lookup_file = os.path.join(model_path, "persaids_lookups.yaml")
    if os.path.exists(model_file) == False or os.path.exists(lookup_file) == False:
        print("ERROR - A model file does not exist")
        return
    
    lookup = Lookup(lookup_file, args.yaml_path, model_path, lookup_path)
    model = Model(model_file, model_path)
    for dts_name in DTSs:
        dts_file = os.path.join(args.dts_path, "DTS_" + dts_name + ".xlsx")
        if os.path.exists(dts_file) == False:
            print("ERROR - DTS_" + dts_name + ".xlsx file does not exist")
            continue
        model.get_dts(dts_file)
        model.get_yaml()
    #for lu in model.lookups:
    #    print(lu[0])
    #    print(lu[1])
    #print(model.yaml)
    model.save()
    lookup.save(model.lookups)
     


if __name__ == '__main__':
    main(sys.argv[1:])

# python3 yaml_modifier.py --dts_path ./dts --yaml_path ../
