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
                invalid_subfield.append('subfield has invalid key: "' + str(key) + '"')
            if isinstance(key, str) and (len(key) != 1):
                invalid_subfield.append('subfield key is not a single char: "' + str(key) + '"')

            val = subfield[key]

            if not isinstance(val, str):
                invalid_subfield.append('subfield value is not a string')


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
            except ValueError as verr:
                problems = []
                for arg in verr.args:
                    problems.append(str(arg))
                if problems:
                    invalid_subfields.append(fieldname + ' and '.join(problems))
    
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
        if (not tag) or (len(tag) != 3) or (not tag.isdigit()):
            invalid_fields.append('invalid tag value: ' + str(tag))

    if not 'ind_1' in marc_datafield:
        invalid_fields.append('MARC datafield has no "ind_1" key')
    else:
        ind_1 = marc_datafield['ind_1']
        if ind_1 and len(ind_1) != 1:
            invalid_fields.append('invalid ind_1 value: ' + str(ind_1))

    if not 'ind_2' in marc_datafield:
        invalid_fields.append('MARC datafield has no "ind_2" key')
    else:
        ind_2 = marc_datafield['ind_2']
        if ind_2 and len(ind_2) != 1:
            invalid_fields.append('invalid ind_2 value: ' + str(ind_2))

    if not 'subfields' in marc_datafield:
        invalid_fields.append('MARC datafield has no "subfields" key')
    else:
        validate_subfields(marc_datafield['subfields'])
        
    if invalid_fields:
        raise ValueError(' and '.join(invalid_fields))


def make_marc_datafield (tag, indc_1=None, indc_2=None, subfields=[]):
    '''`tag` is the 3 digit numeric field code.
    `ind_1` and `ind_2` are the indicators (metadata).
    `subfields` is a list of dicts: key is the subfield code
    (with the conventional '$' demarcator omitted);
    value is the data.
    '''
    retval = {'tag': tag, 'indc_1': ind_1, 'indc_2': ind_2, 'subfields': subfields}
    validate_datafield(retval)
    return retval


def add_subfield(marc_datafield, subfield):
    validate_single_subfield(subfield)
    marc_datafield['subfields'].append(subfield)



test_subfield_list = [
    {'a': 'mmmm'},
    {'a': 8},
    {'a': None},
    {'': ''},
    {None: ''},
    {'6': 'merp'},
    {'aa': 'boop'},
    {'': ''},
    {' ': 'eee'},
    {9: None},
    {None: (56, 33)},
    None,
    'abcde',
    (3,4,5),
    {'a': 'meph', 'b': 'hello'},
    {'a': 7, 'b': 8},
]

test_subfields_plural_list = [
    [{'a': 'mmmm'}],
    [{'a': 'mmmm'}, {'b': 'gggg'}],
    [],
    None,
    (),
    {},
    'hello!',
    ['a', 'b', 'c', 'g'],
    [{'a': 7, 'b': []}],
    [{8: 7, 'b': []}],

]





# import sys

# for subfieldz in test_subfields_plural_list:
#     print
#     print(subfieldz)
#     try:
#         validate_subfields(subfieldz)
#     except ValueError as verr:
#         print(verr)

# print('------------------------------------------------------')
# print

# for subfield in test_subfield_list:
#     print(subfield)
#     try:
#         validate_single_subfield(subfield)
#     except ValueError as verr:
#         print(verr)
#     print


# if (album_json.record_label) {
#     pattern = [
#             ["a", "[Place of publication not indicated] :"],
#             ["b", album_json.record_label + ',']
#     ];
#     if (album_json.release_date) {
#          pattern.push(["c", album_json.release_date.split("-")[0]]);
#     }
# }

testfield = make_marc_datafield ('260', ind_1=' ', ind_2=' ', subfields=[])

print(testfield)
print('OK?')
validate_datafield(testfield)

testsubs = [
    {'a':'[Place of publication not indicated]'},
    {'b': 'Skywitch Records'},
    {'c': '2016'},
]

for testsub in testsubs:
    print('adding ' + str(testsub))
    add_subfield(testfield, testsub)

print
print(testfield)










