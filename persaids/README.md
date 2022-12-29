# Unified Molgenis Data Model for PerSAIDs

## Instructions
To create the files (yamls, lookup csv and setup bash file) for generating the model data structure, launch from /persaids folder:
```
python3 create_model_files.py --dts_path ./dts --yaml_path ../
```
To create the emx excel file for importing the model in Molgenis instance, launch the following command on the root project:
```
yarn emx:build-persaids
```
To import effectively the model in Molgenis instance, launch the following command on the root project:
```
bash setup_psm.sh
```
To coorect excel files to import  create the bash file for importing them, launch from /persaids folder:
```
python3 create_import_data_files.py --data_path ./data
```
Finally you can import data launching from /persaids/data folder:
```
bash import_data_psm.sh
```
