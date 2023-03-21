# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import yaml
from diagrams import Cluster, Diagram
from diagrams.aws.database import DynamodbTable
from classes.utils import study, prefix, file_entities


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--yaml_file', type=str, help='entities yaml file', required=True)
    return parser.parse_args(argv)

def get_ef_entities():
    ef_entities = []
    with open(file_entities) as f:
        ef_entities = [line.split("\t")[1].rstrip().replace(prefix + "_", "") for line in f]
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
    #print(node)
    return node

#MAIN THREAD
def main(argv):
    args = get_args(argv)
    [nodes, ef_nodes, omic_nodes] = get_nodes(args.yaml_file)

    # ---- GRAPH ATTRIBUTES
    #LAYOUT:            circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
    #LAYOUT WORKING:    circo osage sfdp neato
    circo_attr = {
        "layout":"circo",
        "splines":"spline",
        "mindist": "2",
    }
    neato_attr = {
        "layout":"osage",
        "packMode": "clust",
        "pack": "150",
        "fontsize": "40",
    }

    # ---- CLUSTERS ATTRIBUTES
    ef_attr = {
        "bgcolor":"#fcebe8",
        "fontsize": "30",
        #"compound":"true",
    }
    om_attr = {
        "bgcolor":"#edf7d0",
        "fontsize": "30",
        #"compound":"true",
    }

    # ---- NODES ATTRIBUTES
    node_attr = {
        "shape":"ellipse", 
        "height":"0.8",
        "labelloc":"c",
    }

    # ---- DIAGRAM
    with Diagram(study, show=False, direction="TB", graph_attr=neato_attr): #, curvestyle="curved"

        # CLUSTERS
        ef = []
        with Cluster("Eurofever data", graph_attr=ef_attr):
            for index, n in enumerate(ef_nodes):
                var = n['name']
                globals()[f"{var}"] = DynamodbTable(nodeid=var, label=n['label'])
                ef.append(globals()[var])

        omics = []
        with Cluster("Omics data", graph_attr=om_attr):
            for n in omic_nodes:
                var = n['name']
                globals()[f"{var}"] = DynamodbTable(nodeid=var, label=n['label']) #
                omics.append(globals()[var])

        # patients = DynamodbTable(nodeid=pt_name, label=n['label'])
        # pt_name = "patients"
        # ef1 = []
        # with Cluster("Eurofever P2", graph_attr=ef_attr):
        #     for index, n in enumerate(ef_nodes):
        #         if n['name'] != pt_name and index >= round(len(ef_nodes) / 2):
        #             var = n['name']
        #             globals()[f"{var}"] = DynamodbTable(var)
        #             ef2.append(globals()[var])

        # ef2 = []
        # with Cluster("Eurofever P1", graph_attr=ef_attr):
        #     for index, n in enumerate(ef_nodes):
        #         if n['name'] != pt_name and index < round(len(ef_nodes) / 2):
        #             var = n['name']
        #             globals()[f"{var}"] = DynamodbTable(var)
        #             ef1.append(globals()[var])

        # CONNECTION ARROWS
        for n in nodes:
            n_name = n['name']
            for n_from in n['from']:
                globals()[f"{n_from}"] >> globals()[f"{n_name}"]
            for n_to in n['to']:
                globals()[f"{n_name}"] >> globals()[f"{n_to}"]


if __name__ == '__main__':
    main(sys.argv[1:])

# python3 1a_MODEL_DIAGRAM.py --yaml_file ../model/psm.yaml