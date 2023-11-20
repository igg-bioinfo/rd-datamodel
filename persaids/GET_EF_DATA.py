# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
from classes.request import Request
from classes.sample import Sample
from classes.utils import DTSs
from pandas import read_excel
import os

#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--ef_ids', type=str, help='Eurofever ids', required=False)
    parser.add_argument('--ef_ids_file', type=str, help='Eurofever ids file', required=False)
    return parser.parse_args(argv)

#MAIN THREAD
def main(argv):
    request = Request()
    args = get_args(argv)
    ef_ids = args.ef_ids.split(',') if args.ef_ids else []
    ef_ids_file = args.ef_ids_file if args.ef_ids_file else False
    if ef_ids_file:
        if os.path.exists(ef_ids_file):
            df = read_excel(ef_ids_file, sheet_name=0, header=0, dtype=str)
            ef_ids = df['Eurofever ID'].to_list()
        else:
            print(ef_ids_file, " not found!")
            return
    print("Eurofever IDs to search: " + str(len(ef_ids)))

    for dt in DTSs:
        print(dt)
        df = read_excel('./data/DT_' + dt + '.xlsx', sheet_name=0, header=0, dtype=str)
        pt_col = 'patient_id' if 'patient_id' in df.columns else 'TP_patient_id' 
        patients_df = df[(df[pt_col].isin(ef_ids))]
        patients_df.to_excel('./ef_data/DT_' + dt + '.xlsx')
        print("Patients filtered: " + str(len(patients_df)))
        with open('./ef_data/DT_' + dt + '_errors.tsv', "w") as txt:
            for ef_id in ef_ids:
                found = df[df[pt_col] == ef_id]
                if len(found) == 0:
                    txt.write(ef_id + '\n')
    



   
        

if __name__ == '__main__':
    main(sys.argv[1:])

#python3 GET_EF_DATA.py --ef_ids IT0101326,IT0101725,IT0101727,IT0101760,IT0101914,IT0101777,IT0101755,IT0101750,IT0101748,IT0101769,IT0101745,IT0101904,IT0101737,IT0101286,IT0101290,IT0101414,IT0101295,IT0101356,IT0101425,IT0101216,IT0100105,IT0101912,IT0101405,IT0101407,IT0101239,IT0101658,IT0101516,IT0101517,IT0101881,IT0100492,IT0101307,IT0101436,IT0101357,IT0101432,IT0101487,IT0101241,IT0101196,IT0101358,IT0101240,IT0101204,IT0101242,IT0101213,IT0101756 

# python3 GET_EF_DATA.py --ef_ids_file /home/robertocavanna/Downloads/Eurofever_IDs.xlsx
