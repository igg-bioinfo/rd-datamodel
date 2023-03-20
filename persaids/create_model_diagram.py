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
    node['tie'] = []
    for attr in obj['attributes']:
        if 'refEntity' in attr:
            tie = str(attr['refEntity']).replace(prefix + "_", "")
            if tie.startswith('lookups_') == False:
                node['tie'].append(attr['name'])
                # if str(attr['name']).startswith('belongs'):
                #     node['from'].append(tie)
                # else:
                node['to'].append(tie)
    print(node)
    return node

#MAIN THREAD
def main(argv):
    args = get_args(argv)
    [nodes, ef_nodes, omic_nodes] = get_nodes(args.yaml_file)
    # circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
    #circo osage sfdp
    circo_attr = {
        "layout":"circo",
        "splines":"spline",
        "mindist": "2"
    }
    neato_attr = {
        "layout":"osage",
        "packMode": "clust",
        "pack": "150",
        "fontsize": "40"
    }

    ef_attr = {
        "bgcolor":"#fcebe8",
        "fontsize": "30"
        #"compound":"true",
    }
    om_attr = {
        "bgcolor":"#edf7d0",
        "fontsize": "30"
        #"compound":"true",
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
    with Diagram(study, show=False, direction= "TB", graph_attr=neato_attr): #, curvestyle="curved"

        with Cluster("Omics data", graph_attr=om_attr) as cl_omic:
            for n in omic_nodes:
                var = n['name']
                globals()[f"{var}"] = DynamodbTable(nodeid=var, label=n['label']) #
                omics.append(globals()[var])

        with Cluster("Eurofever data", graph_attr=ef_attr) as cl_ef:
            #patients = DynamodbTable(nodeid=pt_name, label=n['label'])
            for index, n in enumerate(ef_nodes):
                #if n['name'] != pt_name:
                    var = n['name']
                    globals()[f"{var}"] = DynamodbTable(nodeid=var, label=n['label'])
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