#!/usr/bin/python

def validate_single_subfield(subfield):
    ''' A MARC subfield is a dict of form {x: str}:
    - a single member
    - with a one-byte key
    - with a string(can be empty) value. String bytes can be encoded as utf-8.
     If the above conditions are not true, this function raises a ValueError
    '''  
    invalid_subfield = []  
    if not isinstance(subfield, dict):
        invalid_subfield.append('subfield is not a dict')
    else:
        # it's got to be a single-member dict
        keyset = subfield.keys()
        if len(keyset) != 1:
            invalid_subfield.append('subfield contains more than one entry')
        for key in keyset:
            if (not key) or (not isinstance(key, str)) or not key.strip():
                invalid_subfield.append('subfield has invalid key: ' + str(key))
            elif len(key) != 1:
                invalid_subfield.append('subfield key is not a single char: ' + str(key))

    if invalid_subfield:
        raise ValueError(' and '.join(invalid_subfield))


def validate_subfields(subfields):
    '''The `subfields` parameter must be a list containing zero or more
    valid MARC subfields.
    '''
    invalid_subfields = []
    if not isinstance(subfields, list):
        invalid_subfields.append('subfields is not a list')

    # empty list is ok, but if it has content, validate
    elif subfields:
        for indx, subfield in enumerate(subfields):
            fieldname = 'subfield[' + str(indx) + ']'
            try:
                validate_single_subfield(subfield)
            except Valuerror as verr:
                problems = ''
                for arg in verr.args:
                    arglist = arg.split(' and ')
                    for argstr in arglist:
                        argst = fieldname + ' ' + argstr
                        problems.append(argstr)
    
    if invalid_subfields:
        raise ValueError(' and '.join(invalid_subfields))


def validate_datafield(marc_datafield):

    if not marc_datafield:
        raise ValueError('MARC datafield is empty or None')

    invalid_fields = []
    if not 'tag' in marc_datafield:
        invalid_fields.append('MARC datafield has no "tag" key')
    else:
        tag = marc_datafield['tag']
        if (not tag) or (len(tag != 3)) or (not isdigit(tag)):
            invalid_fields.append('invalid tag value: ' + str(tag))

    if not 'ind_1' in marc_datafield:
        invalid_fields.append('MARC datafield has no "ind_1" key')
    else:
        ind_1 = marc_datafield['ind_1']
        if ind_1 and len(ind_1 != 1):
            invalid_fields.append('invalid ind_1 value: ' + str(ind_1))

    if not 'ind_2' in marc_datafield:
        invalid_fields.append('MARC datafield has no "ind_2" key')
    else:
        ind_2 = marc_datafield['ind_2']
        if ind_2 and len(ind_2 != 1):
            invalid_fields.append('invalid ind_2 value: ' + str(ind_2))

    if not 'subfields' in marc_datafield:
        invalid_fields.append('MARC datafield has no "subfields" key')
    else:
        validate_subfields(marc_datafield['subfields'])
        
    if invalid_fields:
        raise ValueError(' and '.join(invalid_fields))


def make_marc_datafield (tag, ind_1=None, ind_2=None, subfields=[]):
    '''`tag` is the 3 digit numeric field code.
    `ind_1` and `ind_2` are the indicators (metadata).
    `subfields` is a list of dicts: key is the subfield code
    (with the conventional '$' demarcator omitted);
    value is the data.
    '''
    retval = {'tag': tag, 'ind_1': ind_1, 'ind_2': ind_2, 'subfields': subfields}
    validate_datafield(retval)
    return retval


def add_subfield(marc_datafield, subfield):
    validate_single_subfield(subfield)
    marc_datafield['subfields'].append(subfield)
