# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import csv
import yaml
from diagrams import Cluster, Diagram
from diagrams.aws.database import RDS, DynamodbTable
from diagrams.aws.network import ELB
from classes.utils import study, file_diagram


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--yaml_file', type=str, help='yaml entity file', required=True)
    return parser.parse_args(argv)

def get_omics_data(file):
    with open(file, 'r') as f:
        res = yaml.safe_load(f)
    return res

#MAIN THREAD
def main(argv):
    args = get_args(argv)

    omics = get_omics_data(args.yaml_file)
    data_omics = []
    for entity in omics["entities"]:
        data_omics.append(entity['label'])
        print(entity)

    data_ef = []
    with open(file_diagram) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            if line[0] == "Eurofever":
                data_ef.append(line[1])

            
    ef1 = []
    ef2 = []
    omics = []
    with Diagram(study, show=False):
        patients = RDS("Patients")
        with Cluster("Eurofever P1") as cls1:
            for index, dt in enumerate(data_ef):
                if dt != "Patients":
                    if index < round(len(dt) / 2):
                        ef1.append(DynamodbTable(dt))
        with Cluster("Eurofever P2") as cls2:
            for index, dt in enumerate(data_ef):
                if dt != "Patients":
                    if index >= round(len(dt) / 2):
                        ef2.append(DynamodbTable(dt))
        with Cluster("Omics data") as cls_omics:
            for dt in data_omics:
                omics.append(DynamodbTable(dt))
        ef1 >> patients << ef2
        patients << omics
        #patients << ef2
        #ef1 >> patients << ef2
        #patients >> omics
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 create_model_diagram.py --yaml_file ../model/psm_base.yaml