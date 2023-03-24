# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
from classes.request import Request
from classes.sample import Sample
from classes.utils import set_value
from pandas import read_excel

#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples_xlsx', type=str, help='excel file with samples', required=True)
    return parser.parse_args(argv)

#MAIN THREAD
def main(argv):
    request = Request()
    args = get_args(argv)
    df = read_excel(args.samples_xlsx, sheet_name=0, header=1, dtype=str)
    samples_tot = 0
    samples_not = 0
    for index, row in df.iterrows():
        patient_id = str(row['Eurofever ID'])
        sample_id = str(row['AIT Code'])
        if sample_id != 'nan' and sample_id != '' and patient_id.lower().startswith("n") == False and patient_id.strip() != "":
            sample = Sample(request, sample_id)
            sample.belongsToPatient = patient_id
            sample.localID = set_value(row['local ID patient*   '])
            sample.institute = set_value(row['Institute'])
            #sample.samplingDate = set_value(row['DATE'])
            sample.set_disease(row['Active or Inactive disease (A/I)'])
            sample.set_treated(row['patient Treated or unTreated       (T/unT)'])
            sample.save(request)
            samples_tot += 1
        else:
            samples_not += 1
            if patient_id != "" and patient_id != "nan":
                print("Samples for patient_id '" + patient_id + "' not imported")
    print("Total imported samples: " + str(samples_tot))
    print("Total NOT imported samples: " + str(samples_not))
        

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 6_SAMPLES_IMPORT.py --samples_xlsx ./data/SAMPLES.xlsx