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
from classes.utils import study, prefix, file_diagram


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--yaml_file', type=str, help='yaml entity file', required=True)
    return parser.parse_args(argv)

def get_ef_entities():
    ef_entities = []
    with open(file_diagram) as f:
        ef_entities = [line.rstrip() for line in f]
    return ef_entities


def get_nodes(file):
    ef_entities = get_ef_entities()
    print(ef_entities)
    objs = []
    nodes = []
    ef_nodes = []
    omic_nodes = []
    with open(file, 'r') as f:
        objs = yaml.safe_load(f)
    for obj in objs["entities"]:
        node = get_node(obj)
        if obj["name"] in ef_entities:
            ef_nodes.append(node)
        else:
            omic_nodes.append(node)
        nodes.append(node)
    return [nodes, ef_nodes, omic_nodes]


def get_node(obj):
    node = {}
    node['name'] = obj['name']
    node['label'] = obj['label']
    node['from'] = []
    node['to'] = []
    for attr in obj['attributes']:
        if 'refEntity' in attr:
            tie = str(attr['refEntity']).replace(prefix + "_", "")
            if tie.startswith('lookups_') == False:
                if str(attr['name']).startswith('belongs'):
                    node['from'].append(tie)
                else:
                    node['to'].append(tie)
    return node

#MAIN THREAD
def main(argv):
    args = get_args(argv)
    [nodes, ef_nodes, omic_nodes] = get_nodes(args.yaml_file)
    # circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
    graph_attr = {
    "layout":"circo",
    "compound":"true",
    "splines":"spline",
    }

    node_attr = {
        "shape":"ellipse", 
        "height":"0.8",
        "labelloc":"c"
    }
    ef = []
    ef1 = []
    ef2 = []
    omics = []
    pt_name = "patients"
    global patients
    patients = None
    with Diagram(study, show=False, direction= "TB", curvestyle="curved", graph_attr=graph_attr):
        patients = DynamodbTable(pt_name)

        with Cluster("Omics data"):
            for n in omic_nodes:
                var = n['name']
                globals()[f"{var}"] = DynamodbTable(var)
                omics.append(globals()[var])

        with Cluster("Eurofever data"):
            for index, n in enumerate(ef_nodes):
                if n['name'] != pt_name:
                    var = n['name']
                    globals()[f"{var}"] = DynamodbTable(var)
                    ef.append(globals()[var])

        # with Cluster("Eurofever P2"):
        #     for index, n in enumerate(ef_nodes):
        #         if n['name'] != pt_name and index >= round(len(ef_nodes) / 2):
        #             var = n['name']
        #             globals()[f"{var}"] = DynamodbTable(var)
        #             ef2.append(globals()[var])

        # with Cluster("Eurofever P1"):
        #     for index, n in enumerate(ef_nodes):
        #         if n['name'] != pt_name and index < round(len(ef_nodes) / 2):
        #             var = n['name']
        #             globals()[f"{var}"] = DynamodbTable(var)
        #             ef1.append(globals()[var])

        for n in nodes:
            n_name = n['name']
            for n_from in n['from']:
                globals()[f"{n_from}"] >> globals()[f"{n_name}"]
            for n_to in n['to']:
                globals()[f"{n_name}"] >> globals()[f"{n_to}"]

        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 create_model_diagram.py --yaml_file ../model/psm_base.yaml