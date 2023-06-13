# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import glob
from pandas import read_excel, concat, unique, DataFrame, read_csv, merge, notna
from upsetplot import plot, from_indicators
import numpy as np

msg = ""


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--master_file', type=str, help='samples master file', required=True)
    parser.add_argument('--omics_path', type=str, help='omics source path', required=True)
    return parser.parse_args(argv)


#SET MESSAGE FUNCTIONS
def set_msg(text, is_title = False):
    global msg
    tmp = ""
    tmp += "\n#-" if is_title == 3 else ""
    tmp += "\n#---" if is_title == 2 else ""
    tmp += "\n#--------" if is_title == 1 else ""
    tmp += str(text).upper() if is_title in [1,2] else str(text)
    tmp += "--------" if is_title == 1 else ""
    tmp += "\n"
    msg += tmp

def set_msg_array(txt, array):
    global msg
    tmp = ""
    tmp += "" if txt == "" else txt + ":\n"
    tmp += "\n".join(array) + "\n\n"
    msg += tmp

def set_msg_df(col, df, df_original):
    global msg
    df_tmp = df_original[df_original[col].isin(df[col])][col].value_counts(dropna=False).to_frame()
    count = 0
    tot = len(df_tmp)
    for i, r in df_tmp.iterrows():
        count += r[col]
        if tot < 100 or r[col] > 50:
            set_msg(str(r.name) + ": " + str(r[col]))
    if tot > 0:
        set_msg("Total occurences: " + str(count)+ "\n")

def set_names(cols):
    txt = "field" + ("s" if len(cols) > 1 else "") + " '" + ", ".join(cols) + "'"
    return txt


#DF MANAGE FUNCTIONS
def check_col(col, df_correct, df_original):
    set_msg("Field " + col + "", 2)
    set_msg("The field '" + col + "' has correct format values in " + str(len(df_correct)) + " rows.")
    df_unique = DataFrame(df_original[col].unique(), columns=[col])
    df_excluded = df_unique[~df_unique[col].isin(df_correct[col])]
    set_msg("Unique values excluded for field '" + col + "' are the following " + str(len(df_excluded)) + ":")
    set_msg_df(col, df_excluded, df_original)

def check_duplicates_for_cols(cols, df):
    col_txt = set_names(cols)
    df_dups = df.loc[df.duplicated(subset=cols, keep=False)]
    df_dups.sort_values(by=cols)
    df_dups_unique = unique(df_dups[cols].values.ravel('K'))
    print(df_dups_unique)
    set_msg("The " + col_txt + " is duplicated for " + str(len(df_dups_unique)) + " rows.")
    for col in cols:
        set_msg_df(col, df_dups, df)
    set_msg("\n")
    return df_dups

def check_duplicates_one_col(col, df):
    df_dups = df.loc[df.duplicated(subset=[col], keep=False)]
    df_dups.sort_values(by=[col])
    set_msg("The field '" + col + "' has duplicated " + str(len(df_dups[col].unique())) + " unique values.")
    set_msg_df(col, df_dups, df)
    return df.drop_duplicates(subset=[col])

def df_merge(df1, df2, keys, how='outer'):
    df = merge(df1, df2, how=how, on=keys, indicator=True)
    keys.append("_merge")
    missing_values = df[keys][df['_merge'] != 'both']
    for _, value in missing_values.iterrows():
        txt = ""
        for k in keys:
            txt += k + ": " + str(value[k]) + ", "
        #print(txt)
    df.drop("_merge",axis=1,inplace=True)
    #print("Done\n")
    return df


#------------------------------------------MAIN THREAD------------------------------------------
def main(argv):
    global msg
    args = get_args(argv)

    #------------------SAMPLES MASTER FILE
    c_institute = "Institute"
    c_patient = "Patient"
    c_sample = "Sample"
    c_sample_date = "Sample date"
    c_status = "Status"
    c_treated = "Treatment"
    c_diagnosis = "Diagnosis"
    rename_columns = {'Institute': c_institute, 
                      'Eurofever ID': c_patient, 
                      'ID sample': c_sample, 
                      'Date of sampling': c_sample_date,
                      'Active or Inactive disease (A/I)\nDrop-down Menu': c_status,
                      'patient Treated or unTreated       (T/unT)\nDrop-down Menu': c_treated,
                      'Disease\nDrop-down Menu': c_diagnosis}
    master_columns = [c_institute, c_patient, c_sample, c_sample_date, c_status, c_treated, c_diagnosis]

    df_master = read_excel(args.master_file, sheet_name=0, header=1, dtype=str)
    df_master.rename(columns=rename_columns, inplace=True)
    df_master = df_master[master_columns]
    
    set_msg("sample master file", 1)
    set_msg("Samples file has " + str(len(df_master)) + " rows.")

    #--COLUMN SAMPLE
    df_sample = df_master[(df_master[c_sample].isna() == False) 
                  & (df_master[c_sample].str != "") 
                  & (df_master[c_sample].str.contains(";") == False) 
                  & (df_master[c_sample].str.contains(",") == False)]
    check_col(c_sample, df_sample, df_master)

    #--COLUMN PATIENT
    df_patient = df_master[df_master[c_patient].str.match("^[a-zA-Z]{2}[0-9]{7}$") == True]
    check_col(c_patient, df_patient, df_master)

    #--COLUMN SAMPLE DATE
    df_sample_date = df_master[df_master[c_sample_date].str.match("^[0-9]{4}-[0-9]{2}-[0-9]{2} 00:00:00$") == True]
    check_col(c_sample_date, df_sample_date, df_master)

    #--COLUMN DISEASE STATUS
    df_status = df_master[(df_master[c_status].str.lower() == 'active') | (df_master[c_status].str.lower() == 'inactive')]
    check_col(c_status, df_status, df_master)

    #--COLUMN TREATED
    df_treated = df_master[(df_master[c_treated].str.lower() == 'treated') | (df_master[c_treated].str.lower() == 'untreated')]
    check_col(c_treated, df_treated, df_master)

    #--COLUMN DIAGNOSIS
    df_diagnosis = df_master[~df_master[c_diagnosis].isna()]
    check_col(c_diagnosis, df_diagnosis, df_master)
    set_msg_array("Unique values for field '" + c_diagnosis + "' are", df_diagnosis[c_diagnosis].unique())

    #--SAMPLES WITH CORRECT VALUES
    df_sample_final = df_sample
    df_sample_final.loc[df_sample_final[c_patient].str.match("^[a-zA-Z]{2}[0-9]{7}$") == False, c_patient] = None
    df_sample_final.loc[df_sample_final[c_sample_date].str.match("^[0-9]{4}-[0-9]{2}-[0-9]{2} 00:00:00$") == False, c_sample_date] = None
    df_sample_final.loc[(df_sample_final[c_status].str.lower() != 'active') & (df_sample_final[c_status].str.lower() != 'inactive'), c_status] = None
    df_sample_final.loc[(df_sample_final[c_treated].str.lower() != 'treated') & (df_sample_final[c_treated].str.lower() != 'untreated'), c_treated] = None
    df_nodups = check_duplicates_one_col(c_sample, df_sample_final)
    set_msg("Samples with no duplicates: " + str(len(df_nodups)))
    df_imported = df_nodups[(~df_nodups[c_patient].isna()) & (~df_nodups[c_sample].isna())]
    set_msg("Samples imported (with sample & patient codes correctly related): " + str(len(df_imported)))
    set_msg("\n")

    #------------------OMICS FILES
    prot_name_old = ""
    set_count = 0
    prots = []
    for set_file in glob.glob(os.path.join(args.omics_path, "pt*/*.csv")) + glob.glob(os.path.join(args.omics_path, "pt*/*.tsv")):
        prot_name = str(set_file.split("/")[1]).replace("pt_", "").replace("_", " ")
        df_prot_name = prot_name.replace(" ", "_")

        if prot_name != prot_name_old:
            if set_count > 1:
                df_prot_name_old = prot_name_old.replace(" ", "_")
                for i in range(1, set_count):
                    globals()[f"df_{df_prot_name_old}_0"] = concat([globals()[f"df_{df_prot_name_old}_0"], 
                                                                globals()[f"df_{df_prot_name_old}_{str(i)}"]], axis=0)
                df_final = globals()[f"df_{df_prot_name_old}_0"]
                set_msg("Overall " + prot_name_old.title() + " has " + str(len(df_final)) + " samples.")
                set_msg("Overall " + prot_name_old.title() + " has " + str(len(df_final.columns)) + " features.")
                check_duplicates_one_col(c_sample, df_final)
            
            prots.append(df_prot_name)
            set_msg(prot_name, True)
            set_count = 0

        no_features = False
        if set_file.endswith(".tsv"):
            no_features = True
            set_file = set_file.replace(".tsv", ".samples")
            set_title = os.path.basename(set_file).replace(".csv", "").replace(".tsv", "")
            df_set = read_csv(set_file, header=None, sep="\t")
            df_set.columns = [c_sample]
            df_set.insert(1, 'Has ' + prot_name, 1)
            globals()[f"df_{df_prot_name}_{str(set_count)}"] = df_set.copy()
        else:
            set_title = os.path.basename(set_file).replace(".csv", "").replace(".tsv", "")
            df_set = read_csv(set_file, header=0, sep="\t")
            df_set = df_set.rename(columns={"ID sample": c_sample}, errors="raise")
            globals()[f"df_{df_prot_name}_{str(set_count)}"] = df_set.copy()
            df_set = df_set[[c_sample]]


        set_msg(set_title, 2)
        if no_features:
            set_msg("THERE ARE TOO MUCH FEATURES, WE ONLY CONSIDER IF SAMPLE HAS THIS OMICS")
        set_msg(set_title.title() + " has " + str(len(df_set)) + " samples.")
        set_msg(set_title.title() + " has " + str(len(globals()[f"df_{df_prot_name}_{str(set_count)}"].columns) - 1) + " features.")
        
        check_duplicates_one_col(c_sample, df_set)

        set_msg("Confronting with " + str(len(df_nodups)) + " samples with no duplicates", 3)
        df_matching = df_set[df_set[c_sample].isin(df_nodups[c_sample])][c_sample]
        set_msg("Total matching: " + str(len(df_matching)))
        df_not_matching = df_set[~df_set[c_sample].isin(df_nodups[c_sample])][c_sample]
        set_msg("Not matching: " + str(len(df_not_matching)))
        
        set_msg("Confronting with " + str(len(df_imported)) + " samples with patient code", 3)
        df_matching = df_set[df_set[c_sample].isin(df_imported[c_sample])][c_sample]
        set_msg("Total matching: " + str(len(df_matching)))
        df_not_matching = df_set[~df_set[c_sample].isin(df_imported[c_sample])][c_sample]
        set_msg("Not matching: " + str(len(df_not_matching)) + "\n")

        set_count += 1
        prot_name_old = prot_name

    #------------------OVERALL OMICS
    set_msg("Overall omics", True)
    df_omics = df_nodups.copy()
    for prot in prots:
        df_omics = df_merge(df_omics, globals()[f"df_{prot}_0"], [c_sample], 'left')
    set_msg("Overall omics has " + str(len(df_omics)) + " samples.")
    set_msg("Overall omics has " + str(len(df_omics.columns)) + " features.")
    df_omics_nodups = check_duplicates_one_col(c_sample, df_omics)
    set_msg("Overall omics has " + str(len(df_omics_nodups)) + " unique samples.")

    #------------------UPSET PLOT FOR NOT NULL VALUES
    df_upset = DataFrame(data = df_omics_nodups[c_sample])
    for prot in prots:
        df_upset[prot] = df_omics_nodups[c_sample].isin(globals()[f"df_{prot}_0"][c_sample].unique())
    df_upset[c_patient] = df_omics_nodups[c_sample].isin(df_patient[c_sample].unique())
    df_upset[c_sample_date] = df_omics_nodups[c_sample].isin(df_sample_date[c_sample].unique())
    df_upset = df_upset.replace({False:np.nan,True:1}) #set False to null and True to 1
    df_upset = df_upset[df_upset.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    plot(from_indicators(indicators=notna, data=df_upset.iloc[:,1:]), show_counts=True)
    from matplotlib import pyplot
    pyplot.savefig(os.path.join(args.omics_path, 'overall_omics.png'))  

    #------------------SAVE DFS
    #df_omics[c_sample].to_csv(os.path.join(args.omics_path, 'overall_omics.csv'), sep="\t")

    #------------------REPORT
    #print(msg)
    with open(os.path.join(args.omics_path, 'statistics.txt'), "w+") as f:
        f.write(msg)

      

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 0_STATISTICS.py --master_file data/SAMPLES.xlsx --omics_path files