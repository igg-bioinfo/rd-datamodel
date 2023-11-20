# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import argparse
import os
import glob
from pandas import read_excel, concat, DataFrame, read_csv, merge, notna, Series
from upsetplot import plot, from_indicators
import numpy as np


#VARIABLES
msg = ""
c_institute = "Institute"
c_patient = "Eurofever ID"
c_sample = "Sample"
c_sample_date = "Sample date"
c_status = "Disease status"
c_treated = "Treatment status"
c_diagnosis = "Diagnosis"
c_dna = "DNA PBMCs"
c_serum = "Serum"
c_rna = "RNA"
c_plasma = "Plasma Serum"
c_blood = "Whole blood"
rename_columns = {'Institute': c_institute, 
                    'Eurofever ID': c_patient, 
                    'ID sample': c_sample, 
                    'Date of sampling': c_sample_date,
                    'Active or Inactive disease (A/I)\nDrop-down Menu': c_status,
                    'patient Treated or unTreated       (T/unT)\nDrop-down Menu': c_treated,
                    'Disease\nDrop-down Menu': c_diagnosis,
                    'DNA/PBMCs': c_dna, 
                    'serum ': c_serum, 
                    'RNA': c_rna, 
                    'Plasma/Serum': c_plasma, 
                    'Whole blood': c_blood}
master_columns = [c_institute, c_patient, c_sample, c_sample_date, c_status, c_treated, c_diagnosis,
                  c_dna, c_serum, c_rna, c_plasma, c_blood]


#RETRIEVE THE ARGUMENTS FOR THE PYTHON APPLICATION
def get_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--master_file', type=str, help='samples master file', required=True)
    parser.add_argument('--omics_path', type=str, help='omics source path', required=True)
    return parser.parse_args(argv)


#SET MESSAGE FUNCTIONS
def set_msg(text: str, is_title: bool|int = False):
    global msg
    tmp = ""
    tmp += "\n#-" if is_title == 3 else ""
    tmp += "\n#---" if is_title == 2 else ""
    tmp += "\n\n#--------" if is_title == 1 else ""
    tmp += str(text).upper() if is_title in [1,2] else str(text)
    tmp += "--------" if is_title == 1 else ""
    tmp += "\n"
    msg += tmp

def set_msg_array(txt: str, array: list):
    global msg
    tmp = ""
    tmp += "" if txt == "" else txt + ":\n"
    tmp += "\n".join(array) + "\n"
    msg += tmp

def set_msg_df(col: str, df: DataFrame, df_original: DataFrame, title: str = ""):
    global msg
    tmp = df_original[df_original[col].isin(df[col])][col].value_counts(dropna=False)
    df_tmp = tmp.to_frame()
    count = 0
    tot = len(df_tmp)
    for i, r in df_tmp.iterrows():
        count += r[col]
        if tot < 100 or r[col] > 50:
            set_msg(str(r.name) + ": " + str(r[col]))
    if tot > 0:
        set_msg("Total occurences: " + str(count))
        df_tmp = tmp.rename_axis(col).to_frame('Occurences')
        df_save(df_tmp, (title if title != "" else col).lower().replace(" ", "_"))

def set_names(cols: list):
    txt = "field" + ("s" if len(cols) > 1 else "") + " '" + ", ".join(cols) + "'"
    return txt

def set_msg_matching(df: DataFrame, df_to_confront: DataFrame, sample_descr: str):
    global c_sample
    set_msg("Confronting with " + str(len(df_to_confront)) + " " + sample_descr, 3)
    df_matching = df[df[c_sample].isin(df_to_confront[c_sample])][c_sample]
    set_msg("Total matching: " + str(len(df_matching)))
    df_not_matching = df[~df[c_sample].isin(df_to_confront[c_sample])][c_sample]
    set_msg("Not matching: " + str(len(df_not_matching)))

def set_msg_cols_rows(title: str, df: DataFrame, no_features: bool = False, title_type: bool|int = 2):
    set_msg(title, title_type)
    set_msg(title.title() + " has " + str(len(df)) + " samples.")
    set_msg(title.title() + " has " + str(len(df.columns) - 1) + " features.")
    if no_features:
        set_msg("THERE ARE TOO MUCH FEATURES, WE ONLY CONSIDER IF SAMPLE HAS THIS OMICS")


#DF MANAGE FUNCTIONS
def check_col(col: str, df_correct: DataFrame, df_original: DataFrame, title: str = ""):
    set_msg("Field " + col + "", 2)
    set_msg("The values for the field '" + col + "' are in correct format for " + str(len(df_correct)) + " rows.")
    df_unique = DataFrame(df_original[col].unique(), columns=[col])
    df_excluded = df_unique[~df_unique[col].isin(df_correct[col])]
    set_msg("Unique values excluded for field '" + col + "' are the following " + str(len(df_excluded)) + ":")
    set_msg_df(col, df_excluded, df_original, "excl_" + col)

def check_drops(col: str, df_final: DataFrame, df_set: DataFrame, title: str = ""):
    df_drops = df_set[~df_set[col].isin(df_final[col])][col]
    if len(df_drops) > 0:
        set_msg_array("Values dropped for field '" + col + "' are the following " + str(len(df_drops)), df_drops.to_list())
        df_save(df_drops, "drops_" + title)
    else:
        set_msg("No values has been dropped.")

def check_common_cols(col: str, df_final: DataFrame, df_set: DataFrame, title: str = ""):
    commons = np.intersect1d(df_final.columns, df_set.columns).tolist()
    commons.remove(col)
    if len(commons) > 0:
        set_msg_array("There are " + str(len(commons)) + " common columns", commons)
        suffix = title.lower().replace(" ", "_")
        cols_dict = {}
        for c in commons:
            cols_dict[c] = c + "_" + suffix
        df_set.rename(columns=cols_dict, inplace=True)
    else:
        set_msg("There are no common columns.")
    return df_set

def check_duplicates_one_col(col: str, df: DataFrame, title: str = ""):
    df_dups = df.loc[df.duplicated(subset=[col], keep=False)]
    df_dups.sort_values(by=[col])
    set_msg("The field '" + col + "' has " + str(len(df_dups[col].unique())) + " unique values duplicated.")
    set_msg_df(col, df_dups, df, "dup_" + title)
    return df.drop_duplicates(subset=[col])

def df_merge(df1: DataFrame, df2: DataFrame, keys: list, how: str = 'outer'):
    df = merge(df1, df2, how=how, on=keys, indicator=True)
    keys.append("_merge")
    missing_values = df[keys][df['_merge'] != 'both']
    for _, value in missing_values.iterrows():
        txt = ""
        for k in keys:
            txt += k + ": " + str(value[k]) + ", "
    df.drop("_merge",axis=1,inplace=True)
    return df

def df_save(df: DataFrame, file_name: str):
    global files_path, c_sample
    if isinstance(df, Series):
        df = df.to_frame()
    if isinstance(df, DataFrame) and c_sample in df.columns:
        df = df.set_index(c_sample)
    df.to_csv(os.path.join(files_path, file_name + ".tsv"), sep="\t")


#------------------------------------------MAIN THREAD------------------------------------------
def main(argv):
    global msg, files_path, c_sample
    args = get_args(argv)
    files_path = os.path.join(args.omics_path, 'statistics')
    if os.path.exists(files_path) == False:
        os.makedirs(files_path)

    #------------------SAMPLES MASTER FILE

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
    df_sample_date = df_master[df_master[c_sample_date].str.strip().str.match("^[0-9]{4}-[0-9]{2}-[0-9]{2} 00:00:00$") == True]
    check_col(c_sample_date, df_sample_date, df_master)

    #--COLUMN DISEASE STATUS
    df_status = df_master[(df_master[c_status].str.strip().str.lower() == 'active') | (df_master[c_status].str.strip().str.lower() == 'inactive')]
    check_col(c_status, df_status, df_master)

    #--COLUMN TREATED
    df_treated = df_master[(df_master[c_treated].str.strip().str.lower() == 'treated') | (df_master[c_treated].str.strip().str.lower() == 'untreated')]
    check_col(c_treated, df_treated, df_master)

    #--COLUMN DIAGNOSIS
    df_diagnosis = df_master[df_master[c_diagnosis].isna() == False]
    check_col(c_diagnosis, df_diagnosis, df_master)
    set_msg_array("Unique values for field '" + c_diagnosis + "' are", df_diagnosis[c_diagnosis].str.strip().unique())
    df_save(DataFrame(df_diagnosis[c_diagnosis].str.strip().unique().tolist()), "diagnosis_unique")

    #--COLUMN DNA
    df_dna = df_master[(df_master[c_dna].isna() == False) & (df_master[c_dna].str.strip().str.lower() != "no") 
                       & (df_master[c_dna].str.strip().str.lower().str.contains('sample') == False)]
    check_col(c_dna, df_dna, df_master)

    #--COLUMN SERUM
    df_serum = df_master[(df_master[c_serum].isna() == False) & (df_master[c_serum].str.strip().str.lower() != "no") 
                       & (df_master[c_serum].str.strip().str.lower().str.contains('sample') == False)]
    check_col(c_serum, df_serum, df_master)

    #--COLUMN RNA
    df_rna = df_master[(df_master[c_rna].isna() == False) & (df_master[c_rna].str.strip().str.lower() != "no") 
                       & (df_master[c_rna].str.strip().str.lower().str.contains('sample') == False)]
    check_col(c_rna, df_rna, df_master)

    #--COLUMN PLASMA
    df_plasma = df_master[(df_master[c_plasma].isna() == False) & (df_master[c_plasma].str.strip().str.lower() != "no") 
                       & (df_master[c_plasma].str.strip().str.lower().str.contains('sample') == False)]
    check_col(c_plasma, df_plasma, df_master)

    #--COLUMN WHOLE BLOOD
    df_blood = df_master[(df_master[c_blood].isna() == False) & (df_master[c_blood].str.strip().str.lower() != "no") 
                       & (df_master[c_blood].str.strip().str.lower().str.contains('sample') == False)]
    check_col(c_blood, df_blood, df_master)

    #--SAMPLES WITH CORRECT VALUES
    df_sample_final = df_sample.copy()
    df_sample_final.loc[df_sample_final[c_patient].str.match("^[a-zA-Z]{2}[0-9]{7}$") == False, c_patient] = None
    df_sample_final.loc[df_sample_final[c_sample_date].str.match("^[0-9]{4}-[0-9]{2}-[0-9]{2} 00:00:00$") == False, c_sample_date] = None
    df_sample_final.loc[(df_sample_final[c_status].str.lower() != 'active') & (df_sample_final[c_status].str.lower() != 'inactive'), c_status] = None
    df_sample_final.loc[(df_sample_final[c_treated].str.lower() != 'treated') & (df_sample_final[c_treated].str.lower() != 'untreated'), c_treated] = None
    df_sample_final.loc[(df_master[c_dna].isna() == False) & (df_master[c_dna].str.strip().str.lower() != "no") 
                       & (df_master[c_dna].str.strip().str.lower().str.contains('sample') == False), c_dna] = None
    df_sample_final.loc[(df_master[c_serum].isna() == False) & (df_master[c_serum].str.strip().str.lower() != "no") 
                       & (df_master[c_serum].str.strip().str.lower().str.contains('sample') == False), c_serum] = None
    df_sample_final.loc[(df_master[c_rna].isna() == False) & (df_master[c_rna].str.strip().str.lower() != "no") 
                       & (df_master[c_rna].str.strip().str.lower().str.contains('sample') == False), c_rna] = None
    df_sample_final.loc[(df_master[c_plasma].isna() == False) & (df_master[c_plasma].str.strip().str.lower() != "no") 
                       & (df_master[c_plasma].str.strip().str.lower().str.contains('sample') == False), c_plasma] = None
    df_nodups = check_duplicates_one_col(c_sample, df_sample_final, "Samples in correct format")
    set_msg("Samples with no duplicates: " + str(len(df_nodups)))
    df_pt_samples = df_nodups[(df_nodups[c_patient].isna() == False) & (df_nodups[c_sample].isna() == False)]
    set_msg("Samples with patient codes correctly related: " + str(len(df_pt_samples)))
    set_msg("\n")

    #------------------OMICS FILES
    set_msg("OMICS EXPERIMENT SETS", 1)
    prot_name_old = ""
    df_prot_name_old = ""
    set_count = 0
    prots = []
    for set_file in glob.glob(os.path.join(args.omics_path, "pt*/*.csv")) + glob.glob(os.path.join(args.omics_path, "pt*/*.tsv")):
        prot_name = str(set_file.split("/")[1]).replace("pt_", "").replace("_", " ")
        df_prot_name = prot_name.replace(" ", "_")

        if prot_name != prot_name_old:
            if set_count > 1:
                for i in range(1, set_count):
                    globals()[f"df_{df_prot_name_old}_0"] = concat([globals()[f"df_{df_prot_name_old}_0"], 
                                                                globals()[f"df_{df_prot_name_old}_{str(i)}"]], axis=0)
                df_final = globals()[f"df_{df_prot_name_old}_0"]
                set_msg_cols_rows("Overall " + prot_name_old, df_final)
                df_final = check_duplicates_one_col(c_sample, df_final, prot_name_old)
                set_msg_matching(df_final, df_nodups, "samples with no duplicates")
                #set_msg_matching(df_final, df_pt_samples, "samples with patient code")
                globals()[f"df_{df_prot_name_old}_0"] = df_final
            if df_prot_name_old != "":
                df_save(globals()[f"df_{df_prot_name_old}_0"], "set_" + df_prot_name_old.lower())
            prots.append(df_prot_name)
            set_msg(prot_name, 1)
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

        set_msg_cols_rows(set_title, df_set, no_features)
        df_set = check_duplicates_one_col(c_sample, df_set, set_title)
        set_msg_matching(df_set, df_nodups, "samples with no duplicates")
        #set_msg_matching(df_set, df_pt_samples, "samples with patient code")
        globals()[f"df_{df_prot_name}_{str(set_count)}"] = df_set

        set_count += 1
        prot_name_old = prot_name
        df_prot_name_old = df_prot_name
    
    if df_prot_name_old != "":
        df_save(globals()[f"df_{df_prot_name_old}_0"], "set_" + df_prot_name_old.lower())

    #------------------OVERALL OMICS
    df_omics = df_nodups.copy()
    for prot in prots:
        set_msg(prot + " merge", 2)
        check_drops(c_sample, df_omics, globals()[f"df_{prot}_0"], prot)
        globals()[f"df_{prot}_0"] = check_common_cols(c_sample, df_omics, globals()[f"df_{prot}_0"], prot)
        df_omics = df_merge(df_omics, globals()[f"df_{prot}_0"], [c_sample], 'left')
    set_msg_cols_rows("Overall omics", df_omics, False, 1)
    df_omics_nodups = check_duplicates_one_col(c_sample, df_omics, "Overall omics")
    set_msg("Overall omics has " + str(len(df_omics_nodups)) + " unique samples.")
    df_save(df_omics_nodups, "omics_without_duplicates")

    #------------------UPSET PLOT FOR NOT NULL VALUES
    df_upset = DataFrame(data = df_omics_nodups[c_sample])
    for prot in prots:
        df_upset[prot] = df_omics_nodups[c_sample].isin(globals()[f"df_{prot}_0"][c_sample].unique())
    df_upset[c_patient] = df_omics_nodups[c_sample].isin(df_patient[c_sample].unique())
    df_upset[c_sample_date] = df_omics_nodups[c_sample].isin(df_sample_date[c_sample].unique())
    df_upset[c_diagnosis] = df_omics_nodups[c_sample].isin(df_diagnosis[c_sample].unique())
    df_upset[c_treated] = df_omics_nodups[c_sample].isin(df_treated[c_sample].unique())
    df_upset[c_status] = df_omics_nodups[c_sample].isin(df_status[c_sample].unique())
    df_upset[c_dna] = df_omics_nodups[c_sample].isin(df_dna[c_sample].unique())
    df_upset[c_serum] = df_omics_nodups[c_sample].isin(df_serum[c_sample].unique())
    df_upset[c_rna] = df_omics_nodups[c_sample].isin(df_rna[c_sample].unique())
    df_upset[c_plasma] = df_omics_nodups[c_sample].isin(df_plasma[c_sample].unique())
    df_upset[c_blood] = df_omics_nodups[c_sample].isin(df_blood[c_sample].unique())
    df_upset_tsv = df_upset.copy()
    df_upset = df_upset.replace({False:np.nan,True:1}) #set False to null and True to 1
    df_upset = df_upset[df_upset.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic

    #UPSET ALL DATA
    plot(from_indicators(indicators=notna, data=df_upset.iloc[:,1:]), show_counts=True)
    from matplotlib import pyplot
    pyplot.savefig(os.path.join(files_path, 'overall.png')) 

    df_upset_tsv = df_upset_tsv.replace({False:0,True:1})
    df_upset_tsv = df_upset_tsv[df_upset_tsv.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    df_upset_tsv['Overall total'] = df_upset_tsv.select_dtypes(include='number').sum(axis=1)
    df_upset_tsv['Omics total'] = df_upset_tsv[prots].sum(axis=1)
    df_save(df_upset_tsv, "overall")

    #UPSET OMICS DATA + CLINCAL 
    df_omics_clinical = df_upset.drop([c_dna, c_serum, c_rna, c_plasma, c_blood], axis=1)
    df_omics_clinical = df_omics_clinical[df_omics_clinical.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    plot(from_indicators(indicators=notna, data=df_omics_clinical.iloc[:,1:]), show_counts=True)
    from matplotlib import pyplot
    pyplot.savefig(os.path.join(files_path, 'omics_clinical.png')) 

    df_omics_clinical_tsv = df_upset_tsv.drop([c_dna, c_serum, c_rna, c_plasma, c_blood], axis=1)
    df_omics_clinical_tsv = df_omics_clinical_tsv.replace({False:0,True:1})
    df_omics_clinical_tsv = df_omics_clinical_tsv[df_omics_clinical_tsv.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    df_omics_clinical_tsv['Overall total'] = df_omics_clinical_tsv.select_dtypes(include='number').sum(axis=1)
    df_omics_clinical_tsv['Omics total'] = df_omics_clinical_tsv[prots].sum(axis=1)
    
    df_save(df_omics_clinical_tsv, "omics_clinical")

    #UPSET CLINCAL 
    df_clinical = df_upset.drop(prots, axis=1)
    df_clinical = df_clinical[df_clinical.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    plot(from_indicators(indicators=notna, data=df_clinical.iloc[:,1:]), show_counts=True)
    from matplotlib import pyplot
    pyplot.savefig(os.path.join(files_path, 'clinical.png')) 

    df_clinical_tsv = df_upset_tsv.drop(prots, axis=1)
    df_clinical_tsv = df_clinical_tsv.replace({False:0,True:1})
    df_clinical_tsv = df_clinical_tsv[df_clinical_tsv.iloc[:,1:].sum(axis=1) > 0] #samples with at least 1 omic
    df_clinical_tsv['Overall'] = df_clinical_tsv.select_dtypes(include='number').sum(axis=1)
    df_save(df_clinical_tsv, "clinical")

    #UPSET ONLY OMICS 
    df_only_omics = df_upset[prots]
    df_only_omics = df_only_omics[df_only_omics.sum(axis=1) > 0] #samples with at least 1 omic
    plot(from_indicators(indicators=notna, data=df_only_omics), show_counts=True)
    from matplotlib import pyplot
    pyplot.savefig(os.path.join(files_path, 'only_omics.png')) 

    df_only_omics_tsv = df_upset_tsv[prots]
    df_only_omics_tsv = df_only_omics_tsv.replace({False:0,True:1})
    df_only_omics_tsv = df_only_omics_tsv[df_only_omics_tsv.sum(axis=1) > 0] #samples with at least 1 omic
    df_only_omics_tsv['Overall'] = df_only_omics_tsv.select_dtypes(include='number').sum(axis=1)
    df_save(df_only_omics_tsv, "only_omics")


    #------------------REPORT
    #print(msg)
    with open(os.path.join(files_path, 'statistics.txt'), "w+") as f:
        f.write(msg)

      

if __name__ == '__main__':
    main(sys.argv[1:])

# python3 STATISTICS.py --master_file data/SAMPLES.xlsx --omics_path files