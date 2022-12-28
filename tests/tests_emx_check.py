#'////////////////////////////////////////////////////////////////////////////
#' FILE: tests_emx_check.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-11-25
#' MODIFIED: 2022-02-07
#' PURPOSE: class for unit testing
#' STATUS: stable
#' PACKAGES: yaml
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import yaml

def __keyCheck__(keysToCheck: list, knownKeys: list, emxObject: str, emxObjectName = None):
    """Run Key Check
    Check input keys against a know key set
    
    @param keysToCheck (list) : list of keys to check
    @param knownKeys (list) : list of known keys (i.e., valid)
    @param emxObject (str) : name of the EMX object (packages, entities, attributes, tags)
    """
    
    if not (emxObject in ['packages','entities', 'attributes', 'tags']):
        raise ValueError(f'{emxObject} is unknown.')
    
    errorCount = 0
    for key in keysToCheck:
        if not key in knownKeys:
            errorCount += 1
            msg = f'Key "{key}" is not a valid {emxObject} property'
            if emxObjectName: msg = f'{emxObjectName}: {msg}'
            print(f'\033[91m x {msg} \033[0m')
    
    if errorCount == 0:
        msg = f'all properties are valid'
        if emxObjectName: msg = f'{emxObjectName}: {msg}'
        print(f'\033[92m ✓ \033[0m {msg}')
        
    return errorCount


def __checkEmxPackages__(emx: list = None):
    """Check package level attributes
    Validate all package-level attributes
    
    @param emx (list) : raw contents of an YAML-EMX data model
    """
    keys = emx.keys()
    knownEmxPackageAttribs = [
        'name', 'label', 'description', 'parent', 'tags', # proper EMX attribs
        'version', 'date', 'defaults', 'tagDefinitions', 'entities'  # yamlemxconvert options
    ]
    
    errors = __keyCheck__(
        keysToCheck = keys,
        knownKeys = knownEmxPackageAttribs,
        emxObject = 'packages'
    )
    
    return errors


def __checkEmxEntities__(emx: list = None):
    knownEmxEntityProps = [
        # proper emx
        'name', 'label', 'extends', 'package', 'abstract',
        'description', 'backend', 'tags',
        # yamlemxconvert options
        'attributes'
    ]
    
    if not 'entities' in emx:
        print(f'\033[93m ! \033[0m No entities were defined in the YAML')

    entityErrors = 0
    if 'entities' in emx:
        for entity in emx['entities']:
            errors = __keyCheck__(
                keysToCheck = entity.keys(),
                knownKeys = knownEmxEntityProps,
                emxObject = 'entities',
                emxObjectName = entity['name']
            )
            entityErrors = entityErrors + errors
    return entityErrors
                

def __checkEmxAttributes__(emx):
    knownEmxAttribProps = [
        'entity', 'name', 'dataType', 'refEntity', 'nillable',
        'idAttribute', 'auto', 'description', 'rangeMin', 'rangeMax',
        'lookupAttribute', 'label', 'aggregateable', 'labelAttribute', 'readOnly',
        'tags', 'validationExpression', 'visible', 'defaultValue', 'partOfAttribute',
        'expression', 'enumOptions'
    ]
    
    knownEmxDataTypes = [
        'bool', 'categorical', 'categorical_mref', 'compound', 'date', 'datetime',
        'decimal', 'email', 'enum', 'file', 'hyperlink', 'int', 'long', 'mref',
        'one_to_many', 'string', 'text', 'xref'
    ]
    
    attrErrors = 0
    if 'entities' in emx:
        for entity in emx['entities']:
            if 'attributes' in entity:
                for attr in entity['attributes']:
                    errors = __keyCheck__(
                        keysToCheck = attr.keys(),
                        knownKeys = knownEmxAttribProps,
                        emxObject = 'attributes',
                        emxObjectName = f"{entity['name']}_{attr['name']}"
                    )
                    
                    if 'dataType' in attr.keys():
                        if not (attr['dataType'] in knownEmxDataTypes):
                            msg = f"{entity['name']}_{attr['name']}: dataType \'{attr['dataType']}\' invalid"
                            print(f'\033[91m x {msg} \033[0m')
                    attrErrors = attrErrors + errors
    return attrErrors
    
def checkEmxStructure(file: str = None):
    """Check Emx Structure
    Validates all properties and dataTypes
    
    @param file (str) : location to YAML-EMX file
    """
    
    with open(file, 'r') as stream:
        emx = yaml.safe_load(stream)
        stream.close()
    
    print(f'\033[95m -- Checking EMX Package structure ----------- \033[0m')
    pkgErrors = __checkEmxPackages__(emx = emx)
    
    print(f'\n\033[95m -- Checking EMX Entities Structure ----------- \033[0m')
    entityErrors = __checkEmxEntities__(emx = emx)
    
    print(f'\n\033[95m -- Checking EMX Attributes structure ----------- \033[0m')
    attrErrors = __checkEmxAttributes__(emx = emx)
    
    print('')
    print(f'\033[95m -- Errors Summary ----------- \033[0m')
    if (attrErrors + entityErrors + pkgErrors) > 0:
        print(f'\033[91m Errors detected in model. \033[0m')
        print('')
        print(f'\033[94m   Package: \033[0m {pkgErrors}')
        print(f'\033[94m    Entity: \033[0m {entityErrors}')
        print(f'\033[94m Attribute: \033[0m {attrErrors}')
    else:
        print('\033[92m No errors detected \033[0m')
    
    


#//////////////////////////////////////////////////////////////////////////////

# Test Emx Structure
#checkEmxStructure(file = './src/emx-umdm/umdm_emx1.yaml')
checkEmxStructure(file = './model/psm.yaml')