# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
from classes.model import Model
from classes.lookup import Lookup
from classes.utils import prefix, DTSs, study, file_diagram


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
    schema_file = os.path.join(args.yaml_path, "schemas", study + "_schema.md")
    if os.path.exists(args.dts_path) == False or os.path.exists(model_path) == False or os.path.exists(lookup_path) == False:
        print("ERROR - Some main folder does not exist")
        return
    if os.path.exists(file_diagram):
        os.remove(file_diagram)
    model_file = os.path.join(model_path, prefix + "_base.yaml")
    lookup_file = os.path.join(model_path, prefix + "_base_lookups.yaml")
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
    if os.path.exists(schema_file):
        os.remove(schema_file)
     


if __name__ == '__main__':
    main(sys.argv[1:])

# python3 1_MODEL_FILES.py --dts_path ./dts --yaml_path ../
