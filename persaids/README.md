# PerSAIDs Unified Molgenis Data Model & Import Data from Eurofever

PerSAIDs data model is created starting from a fork of the Unified Molgenis Data Model.
The first steps are about to recreate clinical data structure from Eurofever export files in the yaml files where previously omics related tables were manually added, and subsequently to import these data in the new structure with Molgenis mcmd software.
All omics data are imported as files (experiment sets) and connected to the correct samples through ad hoc scripts.

## Instructions
First of all, you need to install [mcmd](https://github.com/molgenis/molgenis-tools-commander/wiki/Installation-guide) and configure it: set your Molgenis server and admin credentials.
After that you'll be able to connect to your Molgenis instance.


For changing model structure outside Eurofever, remember to change for entities: 
**psm_base.yaml**
and for lookups:
**psm_base_lookups.yaml**


**STEP 1 - CREATE FILES FOR MODEL STRUCTURE**

To re\create the files (yamls, lookup csv and setup bash file) for generating the model data structure, launch from **/persaids** folder:
```
python3 1_MODEL_FILES.py --dts_path ./dts --yaml_path ../
```
After that, you can generate a diagram for the model data structure too, launching: ```python3 1a_MODEL_DIAGRAM.py --yaml_file ../model/psm.yaml```

**STEP 2 - ELABORATE FILES FOR MODEL STRUCTURE**

To create the emx excel file for importing the model in Molgenis instance, launch the following command:
```
yarn emx:build-persaids
```

**STEP 3 - IMPORT MODEL STRUCTURE**

You can delete manually to delete previous model structure of PerSAIDs (psm) even if **3_MODEL_IMPORT** does it already: ```yarn m:delete-persaids```
To import effectively the model in Molgenis instance, launch the following command from **/persaids** folder:
```
bash 3_MODEL_IMPORT.sh
```

**---- EUROFEVER DATA IMPORT ----**

**STEP 4 - CREATE FILES FOR EUROFEVER DATA IMPORT**

To normalize excel files and to create the bash file for importing them, launch from **/persaids** folder:
```
python3 4_EF_IMPORT_FILES.py --data_path ./data
```

**STEP 5 - IMPORT EUROFEVER DATA**

Finally you can import data launching from **/persaids** folder:
```
bash 5_EF_IMPORT.sh
```

**---- OMIC DATA IMPORT ----**

To import all other data outside Eurofever, we need a **/persaids/files/credentials.py** with this content:
```
host = ""

username = ""

password = ""
```

**STEP 6 - IMPORT SAMPLES**

Import samples launching from **/persaids** folder:
```
python3 6_SAMPLES_IMPORT.py --samples_xlsx ./data/SAMPLES.xlsx
```

**STEP 7 - IMPORT EXPERIMENT SETS**

Protocols for files are created according to folder (ex. /pt_OLINK_V1).
To import files related to samples and protocols, launch from **/persaids** folder:
```
python3 7_SETS_IMPORT.py --files_path ./files
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
