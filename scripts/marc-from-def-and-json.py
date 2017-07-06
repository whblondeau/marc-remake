#!/usr/bin/python
# so "/" vs "//" integer division will behave the same 
# in python 2 and 3.
# imports from __future__ must be at the head of the file,
# which is why this is here.
from __future__ import division

import copy


# Constants for subfield expression parse operations
opaque_delims = {'"': '"', "'": "'"}
nestable_delims = {'(':')', '[':']', '{':'}'}



# =============================================================================
#
# ================== GENERAL UTILITIES ========================================


def read_indent(line):
    indx = -1
    if not line.strip():
        return indx

    for char in line:
        indx += 1
        if char.strip():
            return indx

# def compose_multiple_sublistings(content_nodes, listing_subfields):
#     for 



# =============================================================================
#
# ================== PARSING MARCEXPORT.DEFINE INTO A DATA STRUCTURE ==========


def parse_marcexport_deflines(deflines):
    '''This function turns the marcexport define content into datastructures.

    It reads a map of of text line blocks that have been read from
    a MARC export definition. The names of the blocks correspond to the
    purpose of the information in the blocks.

    From those, it parses source content for the different
    categories of information. (It ignores "DESCRIPTION", which is
    non-machine-parseable documentation for humans.)
    
    From the content, it parses a dictionary/map/hash/object of marcexport
    datastructures:
        - 'known_parameters', required parameters
        - 'functions', function names anb brief signature/descriptions
        - 'json_value_exprs', named expressions for pulling values from a
            JSON instance.
        - 'field_templates', an ordered sequence of data structures listing
            desired fixed values and extractiono expression for MARC fields.
            This list of templates thus controls field order, subfield order,
            and instructions for pulling data from the expected JSON instance.

    This marcexport datastructures dictionary/map/hash/object is returned.
    '''
    defblocks = {}
    current_blockname = None

    for line in deflines:
        if line.strip().endswith('--------'):
            line = line.strip()
            current_blockname = line[:line.find('----')]
            current_blockname = current_blockname.lower().replace(' ', '_')
            defblocks[current_blockname] = []

        else:
            if current_blockname:
                defblocks[current_blockname].append(line.strip())

    print(str(len(defblocks)) + ' blocks read in.')
    for block in defblocks:
        print(block + ' (' + str(len(defblocks[block])) + ' lines)')
    print

    # now evaluate marcexport define DATASTRUCTURE content as required
    marcdefs = {}


    # KNOWN PARAMETERS:
    # what needs to be passed in for some things to work -- 
    # in codebase, some are environment variables;
    # at command line, they must be explicitly passed.
    paramnames = []
    for line in defblocks['known_parameters']:
        if line.strip():
            paramnames.append(line.strip())

    marcdefs['known_parameters'] = paramnames


    # FUNCTIONS:
    # function names and expressions
    marcdefs['functions'] = {}
    for line in defblocks['functions']:
        line = line.strip()
        if line:
            # extract the function name
            funcname = line.split('(')[0]
            marcdefs['functions'][funcname] = line


    # EXTRACTORS:
    # expressions for pulling data out of JSON instances
    marcdefs['json_value_exprs'] = {}
    for line in defblocks['json_extracted_properties']:
        line = line.strip()
        parts = line.split('=')
        # someone might put some equals signs in the expr - condition or something
        marcdefs['json_value_exprs'][parts[0].strip()] = ('='.join(parts[1:])).strip()


    # TEMPLATES: 
    # ordered sequence of templates for MARC fields
    marcdefs['field_templates'] = None

    field_data = [] # list of MARC field data assembled according to definitions
    current_field = None

    # using a while loop to have control over indx for readaheads
    indx = -1
    while indx < len(defblocks['export_define']) - 1:

        indx += 1
        line = defblocks['export_define'][indx]

        # indented_line is for processing indents. Otherwise, just strip
        # the line completely.
        indented_line = line.rstrip()
        line = line.strip()

        if line.endswith('----'):
            # just a header
            continue

        if not line:
            # blank line --> field is done
            if current_field:
                # data structures need a copy
                field_data.append(copy.copy(current_field))
                current_field = None

        if line.startswith('FIELD:'):
            # new field
            current_field = {}
            fieldtag = line.split(':')[1].strip()
            current_field['tag'] = fieldtag

        elif line.startswith('INDC1:'):
            indc1 = line.split(':')[1].strip()
            if indc1 == 'blank':
                indc1 = ' '
            current_field['indicator_1'] = indc1

        elif line.startswith('INDC2:'):
            indc2 = line.split(':')[1].strip()
            if indc2 == 'blank':
                indc2 = ' '
            current_field['indicator_2'] = indc2

        elif line.startswith('FOR EACH:'):
            # more complicated
            foreachexpr = line.split(':')[1].split(' in ')
            current_field['foreach'] = {}
            current_field['foreach']['eachitem'] = foreachexpr[0]
            current_field['foreach']['itemsource'] = foreachexpr[1]

        elif line.startswith('EACH-SUBFIELD:'):
            if 'subfields' not in current_field['foreach']:
                current_field['foreach']['subfields'] = []
            eachsub_code = line.split(':')[1].strip()
            eachsub_expr = defblocks['export_define'][indx + 1].strip()
            current_field['foreach']['subfields'].append({eachsub_code: eachsub_expr})

        elif line.startswith('SORT BY:'):
            # we may one day want to support "sort by a, b" expressions...
            # so make this an array, also
            if 'sortby' not in current_field['foreach']:
                current_field['foreach']['sortby'] = []
            sortby_expr = line.split(':')[1].strip()
            current_field['foreach']['sortby'].append(sortby_expr)

        elif line.startswith('DEMARC-WITH:'):
            demarc_expr = line.split(':')[1].strip()
            current_field['foreach']['demarcator'] = demarc_expr

        # we do not want to grab subfields that are within a 
        elif line.startswith('SUBFIELD:'):
            if 'subfields' not in current_field:
                current_field['subfields'] = []
            subfield_code = line.split(':')[1].strip()
            subfield_expr = defblocks['export_define'][indx + 1].strip()
            current_field['subfields'].append({subfield_code: subfield_expr})

    marcdefs['field_templates'] = field_data

    return marcdefs


def read_marcexpdef_file(marcexpdef_file):
    '''This function reads the marcexport define file, sends the file's
    content to `parse_marcexport_deflines`, and returns the resulting
    operational datastructures. 
    '''
    if not os.path.exists(marcexpdef_file):
        raise TypeException('Parameter `' + marcexpdef_file + '` does not exist.')
    if not os.path.isfile(marcexpdef_file):
        raise ValueException('Parameter `' + marcexpdef_file + '` is not a readable file.')

    deflines_file = open(marcexpdef_file)
    deflines = deflines_file.readlines()
    deflines_file.close()

    retval = parse_marcexport_deflines(deflines)

    return retval





# =============================================================================
#
# ================== EXPRESSION FUNCTIONS CALLABLE IN MARCEXPORT.DEFINE =======

# And their helper functions


def normalize_date(dateval):
    if not dateval:
        return ''
    dateval = str(dateval)
    dateval = dateval.split('T')[0]
    return dateval


def biblio_name(person_name):
    if ',' not in person_name:
        name_segments = person_name.split()     # split on spaces
        if len(name_segments) > 1:
            person_name = ','.join(name_segments[-1], name_segments[:-1])
    return person_name


def release_year(release_date):
    return str(release_date).split('-')[0]


def release_decade(release_date):
    decade_string = release_date.split("-")[0][0:3]    # first 3 chars of year
    decade_number = parseInt(decade_string)
    decade_literal = str(decade_number) + "1-" + str(decade_number + 1) + "0";
    return decade_literal

    

def pretty_comma_list(listexpr, oxford=False):
    '''Accepts a comma separated list in string form, and a boolean
    that, if set to True, will stipulate use of the Oxford comma.
    Returns the list with leading and trailing whitespace stripped from 
    list items, separated by commas, with " and " inserted in lieu of
    the final separator.'''

    last_sep = ' and '
    if oxford:
        last_sep = ', and '

    listexpr = map(strip, listexpr.split(','))
    if len(listexpr) == 1:
        return listexpr(0)

    return ', '.join(listexpr[:-1]) + last_sep + listexpr[-1]


def zeropad(chars, length):
    retval = '0' * length
    # print('zeropad retval: ' + retval)
    retval = retval + chars
    # print('zeropad retval: ' + retval)
    return retval[-length:]


def h_m_s(duration_in_float_seconds):
    '''This function takes a high-precision number in seconds
    (e.g. 364.61401360544215) and returns an h:m:s value
    '''
    hours = 0
    minutes = 0
    seconds = 0

    seconds = int(round(duration_in_float_seconds))
    # print('raw integer seconds: ' + str(seconds))

    hours = seconds // 3600
    if hours:
        seconds -= hours * 3600

    minutes = seconds // 60
    if minutes:
        seconds -= minutes * 60

    retval = ':' + zeropad(str(seconds), 2)
    if minutes:
        if hours:
            retval = ':' + zeropad(str(minutes), 2) + retval
        else:
            retval = str(minutes) + retval
    if hours:
        retval = str(hours) + ':' + retval

    return retval


def render_duration(duration_in_float_seconds):
    return '(' + h_m_s(duration_in_float_seconds) + ')'


def total_play_length(tracks):
    float_seconds = 0.0
    for track in tracks:
        float_seconds += track['duration']
    return h_m_s(float_seconds)





# =============================================================================
#
# ================== SUBFIELD EXPRESSION PARSING FUNCTIONS ====================

# This is a simplistic stack-based recursive descent parse with implicit
# grammar for subfield expressions in marcexport.define. 
# The "delims" structure is a stack which grows as new opening delimiters
# occur, and shrinks as corresponding closing delimiters occur.
#
# In a subfield expression, quoted string literals are opaque objects: it
# doesn't matter what characters they contain, except the occurrence of
# the same quote character that begain the literal.
#
# The other kind of delimiter is the nestable structure token: (, [, {
# that open a nested sequence, and the corresponding ), ], } delimiters.
# As the name suggests, these kinds of delimiters can be meaningfully
# nested
#
# The parse separates the expression into syntactilly significant 
# character sequences, as noted in the `tokenize` function string.


def closes_delim(delims, char, opaques=opaque_delims, nestables=nestable_delims):
    '''Returns True if char closes LAST value in delims'''
    if not delims:
        # Nothing to close
        return False

    # the last character in a delim sequence is looking for its closure
    openchar = delims[-1]

    if openchar in opaques:
        # We are in a string literal. Nothing but the corresponding 
        # close quote will have any effect.
        return (char == opaques[openchar])
    if openchar in nestables:
        # We're in a nestable expression
        if char == nestables[openchar]:
            # It's the right one
            return True
        elif char in nestables.values():
            # It's a wrong one. Invalid nesting!
            errmsg = 'BAD SUBFIELD EXPR: closing character `' + char
            errmsg += '` does not match opening character `' + openchar + '`.'
            raise Exception(errmsg)
    else:
        # Neither opaque nor nestable. Fix the tokenize script
        errmsg = 'CODE ERROR: invalid delimiter `' + delims[-1] + '`.'
        errmsg += ' Probably in tokenize function.'
        raise Exception(errmsg)

    return False


def opens_delim(delims, char, opaques=opaque_delims, nestables=nestable_delims):
    if not delims:
        # any opening delim will start a block
        return char in opaques or char in nestables

    if delims[-1] in opaques:
        # We are in a string literal, so no delimiter can open a nested block. 
        # This is what "opaque" means. A quoted literal can contain anything;
        # opening delimiters are insignificant.
        return False
    elif delims[-1] in nestables:
        # We're in a nested block. We can open either a string literal 
        # or a nested block here.
        return char in opaques or char in nestables
    else:
        # Neither opaque nor nestable. Fix the tokenize script
        errmsg = 'CODE ERROR: invalid delimiter `' + delims[-1] + '`.'
        errmsg += ' Probably in tokenize function.'
        raise Exception(errmsg)


def append_normalized_block(block, blocks):
    '''Normalizes whitespace; will not append a whitespace-only block.'''
    if block.strip():
        blocks.append(block.strip())


def tokenize(expr, opaques=opaque_delims, nestables=nestable_delims):
    '''This function returns the `expr` argument divided into a sequence of
    syntactically significant blocks of characters. Block types are:
     - string literals, explicitly quoted (treated as "opaque" to further parsing)
     - opening and closing nestable structure tokens: (, [, {, ), ], }
     - concatenation symbol: + with adjacent whitespace preserved
     - function names, invoked at JSON --> MARC export time
     - extracted property names, resolved at JSON --> MARC export time
    Concatenating the blocks in this return value recreates the `expr`
    parameter. This is a lossless transformation. 
    '''
    top_blocks = []     # sequence of blocks
    current_block = ''
    current_delims = []

    for char in expr:

        if closes_delim(current_delims, char):
            # we are matching an earlier opening. If quote, no thing.
            # if nestable... a little more involved.
            if char in opaques.values():
                # append it. Quotes don't get their own block like nestables do
                current_block += char
                append_normalized_block(current_block, top_blocks)

            elif char in nestables.values():
                append_normalized_block(current_block, top_blocks)
                # closing char gets its own block
                top_blocks.append(char)

            # reset
            current_block = ''
            current_delims.pop()

        elif opens_delim(current_delims, char):

            if char in nestables:
                append_normalized_block(current_block, top_blocks)
                # it gets its own block
                top_blocks.append(char)
                # reset
                current_block = ''
                current_delims.append(char)

            elif char in opaques:
                append_normalized_block(current_block, top_blocks)
                # put the char at the start of the new block
                current_block = ''
                current_block += char
                current_delims.append(char)

        elif char == '+':
            # give this a block of its own, but make no delim entry
            # because this is an operator
            append_normalized_block(current_block, top_blocks)
            # normalize whitespace for operator
            top_blocks.append(' + ')
            current_block = ''

        else:
            # non-delim, non-operator: content only:
            # neither opens nor closes
            current_block += char

    # flush accumulated content to return value
    append_normalized_block(current_block, top_blocks)

    return top_blocks






# =============================================================================
#
# ================== CORE FUNCTIONS FOR EXPORTING MARC RECORDS ================


def compute_extracts(extract_block, jsonobj):
    print('COMPUTING EXTRACTS.')
    print(extract_block)
    print
    retval = {}
    album_json = jsonobj
    for propname in extract_block:
        if not propname:
            # empty key got in. gotta fix the parse
            continue
        print(propname + ':')
        print(extract_block[propname])
        extracted_val = eval(extract_block[propname])
        print(extracted_val)
        retval[propname] = extracted_val
    return retval


def compute_foreach(foreach_template, json_extracts,
    defined_functions, defined_parameters, 
    opaques=opaque_delims, nestables=nestable_delims):
    '''This function accepts a template object for a FOR EACH: directive
    from a marcexport define. 

    The template object has the structure:
        {
            'eachitem': <str: json node name>,                  //for tracks, 'track'
            'itemsource': <array of json nodes with that name>,
            'subfields': <array of single-val {code: expr} dicts>,
            'sortby': <array of property exprs>,
            'demarcator': a string to be inserted between items
        }
    '''
    # convenience variables for template expressions
    item = foreach_template['eachitem']
    sourcenode = foreach_template['itemsource']
    itemsubfields = foreach_template['subfields']
    itemsortkey = foreach_template['sortby']
    demarcator = foreach_template['demarcator']

    # array to hold items as they are composed
    composed_items = []

    # apply extraction
    for item in sourcenode:
        itemcontent = {}
        itemcontent['subfields'] = itemsubfields
        itemcontent['sortkey'] = foreach_template['sortby']
        composed_items.append(extracts)




def compute_subfield_expr(expr, json_extracts, defined_functions, defined_parameters,
    opaques=opaque_delims, nestables=nestable_delims):
    retval = expr

    # this is a parse 
    tokens = tokenize(expr)
    for indx, token in enumerate(tokens):
        if token[0] in opaques:
            # this is a string literal. Don't mess with it.
            continue

        # replace reference to extract name with actual value extracted from JSON.
        # ensure that the result is quotes as a literal.
        for extract in json_extracts:
            if extract in token:
                # print('token before json extract fix: ' + token)
                extractval = json_extracts[extract]
                if isinstance(extractval, str):
                    # direct substitution
                    token = token.replace(extract, '"' + extractval + '"')
                # print('token after json extract fix: ' + token)
                # print

        for param in defined_parameters:
            if param in token:
                # print('token before param fix: ' + token)
                paramval = defined_parameters[param]
                if isinstance(paramval, str):
                    # direct substitution
                    token = token.replace(param, '"' + paramval + '"')
                # print('token after param fix: ' + token)
                # print

        # sanity on function call in expr
        if token == '(':
            # this opens a function.
            # What function name was the previous token?
            funcname = tokens[indx - 1]
            if funcname not in defined_functions:
                print('function name `' + funcname + '` not in functions in MARC export definition.')

    # concat tokens into content
    evaluable = ''.join(tokens)

    # print('evaluating:')
    # print(evaluable)

                    
    retval = evaluable
    # retval = eval(evaluable)
    # print('evaluated to:')
    # print(retval)

    return retval



usage = '''
USAGE: marc-from-def-and-json <marc def file> <json_file> <collection name> <collection host>
'''

# The sequence of operation in batch mode is:
# - parse the marc define file into operational data structures
# - parse the json source
# - extract the JSON properties
# - for each field in the 'field_templates' datastructure,:
#       - copy the field datastructure
#       - evaluate the subfield content for each field, substituting the
#           final string value for the expr



import sys
import os, os.path
import json
import datetime

if '--help' in sys.argv:
    print(usage)
    exit(0)

call_options = [arg for arg in sys.argv[1:] if arg.startswith('-')]
call_params = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

def_filename, json_filename, collection_name, collection_host = call_params[:4]

print('MARC export definition file:')
print('    ' + def_filename)
print('JSON sourcefile:')
print('    ' + json_filename)
print('Collection namespace:')
print('    ' + collection_name)
print('Hostname:')
print('    ' + collection_host)

if not os.path.isfile(def_filename):
    print('FATAL ERROR: ' + 'MARC export definition "' + def_filename + '" is not a file.')
    print(usage)
    exit(1)

if not os.path.isfile(json_filename):
    print('FATAL ERROR: ' + 'JSON sourcefile "' + json_filename + '" is not a file.')
    print(usage)
    exit(1)

print('OK STILL HERE')

# still here
export_definitions = read_marcexpdef_file(def_filename)

print('EXPORT DEFINITIONS PARSED SUCCESSFULLY')

print
print('What do we have?')
for deftype in export_definitions:
    print(deftype)
    print(str(len(export_definitions[deftype])) + ' data items:')
    if deftype != 'field_templates':
        for item in export_definitions[deftype]:
            print(item)

    print


print
jsonsource = None
with open(json_filename) as json_file:
    jsonsource = json_file.read()
    json_file.close()

jsonobj = json.loads(jsonsource)

print('JSON parsed successfully.')

print
print('BLOCKS:')
for key in export_definitions:
    print(key)

parameters_structure = export_definitions['known_parameters']
extracts_structure = export_definitions['json_value_exprs']
functions_structure = export_definitions['functions']
extracted_properties = compute_extracts(extracts_structure, jsonobj)
# for propname in json_properties:
#     print(propname + ': ' + str(json_properties[propname]))
print('property values successfully extracted from JSON.')

print
print('EXTRACTED PROPERTIES:')

for property in extracted_properties:
    print
    print(property)
    print(extracted_properties[property])

print


print('FIELD DATA:')
for marcfield in export_definitions['field_templates']:
    print
    print('tag: ' + marcfield['tag'])
    print('ind_1: ' + marcfield['indicator_1'])
    print('ind_2: ' + marcfield['indicator_2'])
    if 'subfields' in marcfield:
        for subfield in marcfield['subfields']:
            print(subfield)
            subcode = subfield.keys()[0]
            subval = subfield[subfield.keys()[0]]
            print('  ' + subcode + ': ' + subval)
            sub_eval = compute_subfield_expr(subval, extracted_properties, functions_structure, parameters_structure)
            print('  ' + subcode + ': ' + sub_eval)

    # current_field['foreach']['eachitem'] = foreachexpr[0]
    # current_field['foreach']['itemsource'] = foreachexpr[1]
    # current_field['foreach']['sortby'].append(sortby_expr)
    # current_field['foreach']['demarcator'] = demarc_expr
    if 'foreach' in marcfield:
        print('FOREACH YES')
        if 'eachitem' in marcfield['foreach']:
            print('  foreach ' + marcfield['foreach']['eachitem']) 
        if 'itemsource' in marcfield['foreach']:
            print('  in ' + marcfield['foreach']['itemsource'] + ':')
        if 'subfields' in marcfield['foreach']:
            print('  SUBFIELDS YES')
            for subfield in marcfield['foreach']['subfields']:
                print('    ' + str(subfield))
        if 'sortby' in marcfield['foreach']:
            print('  SORTBY YES')
            print('    ' + str(marcfield['foreach']['sortby']))
        if 'demarcator' in marcfield['foreach']:
            print(' DEMARCATOR YES')
            print('    ' + marcfield['foreach']['demarcator'])
