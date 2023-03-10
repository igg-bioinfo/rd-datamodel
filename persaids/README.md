# PerSAIDs Unified Molgenis Data Model & Import Data from Eurofever

## Instructions
First of all, you need to install [mcmd](https://github.com/molgenis/molgenis-tools-commander/wiki/Installation-guide) and configure it: set your Molgenis server and admin credentials.
After that you'll be able to connect to your Molgenis instance.


To create the files (yamls, lookup csv and setup bash file) for generating the model data structure, launch from **/persaids** folder:
```
python3 create_model_files.py --dts_path ./dts --yaml_path ../
```
To create the emx excel file for importing the model in Molgenis instance, launch the following command on the **root** project:
```
yarn emx:build-persaids
```
To import effectively the model in Molgenis instance, launch the following command on the **root** project:
```
bash setup_psm.sh
```
To normalize excel files and to create the bash file for importing them, launch from **/persaids** folder:
```
python3 create_import_data_files.py --data_path ./data
```
Finally you can import data launching from **/persaids** folder:
```
bash import_data_psm.sh
```
To import file we need a **/persaids/files/credentials.py** with this content:
```
host = ""

username = ""

password = ""
```

# Biobank management

## Import molgenis-app-biobank-explorer
Clone the repository
```
git clone https://github.com/molgenis/molgenis-app-biobank-explorer.git
```
Move to the cloned folder
```
cd molgenis-app-biobank-explorer
```
Build the app to be imported in Molgenis.
Yarn can be easily installed with conda/mamba, e.g.:
```
# mamba create --name yarn -c conda-forge yarn
# conda activate yarn
```
```
yarn build
```

If you get the ```ERR_OSSL_EVP_UNSUPPORTED``` error, try the next command (suggested [here](https://stackoverflow.com/questions/69394632/webpack-build-failing-with-err-ossl-evp-unsupported)):
```
export NODE_OPTIONS=--openssl-legacy-provider
``` 

Upload in Molgenis:
 - ```dist/molgenis-app-biobank-explorer.v7.22.0.zip``` (Plugins -> App manager)
 - ```sample-data/BBMRI-ERIC_model_Tags.xlsx``` (Import data -> Advanced data import)
 - ```sample-data/BBMRI-ERIC_model.xlsx``` (Import data -> Advanced data import)
