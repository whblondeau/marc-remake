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
# ================== UTILITY FUNCTIONS ========================================

def evaluate_parameter(param):
    '''if the parameter is a filename, read the file and return its content.
    Otherwise, return the parameter unaltered.
    '''
    retval = param
    if os.path.isfile(param):
        value_file = open(param)
        retval = value_file.read()
        value_file.close()
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
    '''Wrapper function that coerces representation to float
    (because JSON might wrap value in quotes) and rounds it to
    standard hours, minutes, seconds representation.
    '''
    return '(' + h_m_s(duration_in_float_seconds) + ')'


def total_play_length(tracks):
    float_seconds = 0.0
    for track in tracks:
        float_seconds += track['duration']
    return h_m_s(float_seconds)





# =============================================================================
#
# ================== SUBFIELD EXPRESSION PARSING FUNCTIONS ====================

# In MARC fields, the "tag", "indicator 1", and "indicator 2" values are
# fixed; their values are defined in the MARCout export definition.
#
# Subfield content, on the other hand, often includes values extracted from 
# the album JSON

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
    '''Strips leading & trailing whitespace; will not append a whitespace-only block.'''
    if block.strip():
        blocks.append(block.strip())


def tokenize(expr, opaques=opaque_delims, nestables=nestable_delims):
    '''This function returns the `expr` argument divided into a sequence of
    syntactically significant blocks of characters.

    Block types are:
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
    # print('COMPUTING EXTRACTS.')
    # print(extract_block)
    # print
    retval = {}
    album_json = jsonobj
    for propname in extract_block:
        if not propname:
            # empty key got in. gotta fix the parse
            continue
        # print(propname + ':')
        # print(extract_block[propname])
        extracted_val = eval(extract_block[propname])
        # print(extracted_val)
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


# =============================================================================
#
# ================== CONSTANTS ================================================



usage = '''export-marc.py <marcout-defn-structure> <record-to-export>
    <collection_ns> <collection_hostname> [--verbose]

PARAMETERS:

    marcout-defn-structure: 
        The serialized datastructure emitted by the MARCout parse.

    record-to-export:
        A JSON representation of the album being exported.

    collection_ns:
        The Rabble-style namespace for the collection to which the record
        belongs. Needed for certain MARC records; not available in JSON.

    collection_hostname:
        The official URL at which the collection is published. Needed for
        certain MARC records; not available in JSON.

    --verbose: 
        Human-friendly output. Not suitable for command line piping.

RETURNS:
    A serialized data structure representing a MARC record:

        of the form defined in <marcout-defn-structure>;

        with record-specific content extracted from <record-to-export>;

        with additional content from <collection_ns> and <collection_hostname>,
            as required.

'''



# =============================================================================
#
# ================== EXECUTE SCRIPT ===========================================



import sys
import os, os.path
import json
import datetime

if '--help' in sys.argv:
    print(usage)
    exit(0)

call_options = [arg for arg in sys.argv[1:] if arg.startswith('-')]
call_params = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

marcout_defn_structure, record_to_export, collection_ns, collection_hostname = call_params[:4]

verbose = '--verbose' in call_options

marcout_content = evaluate_parameter(marcout_defn_structure)

export_record_content = evaluate_parameter(record_to_export)


if verbose:
    print('MARC export definition:')
    print('    ' + marcout_content)

    print('JSON record:')
    print('    ' + export_record_content)

    print('Collection namespace:')
    print('    ' + collection_ns)
    print('Hostname:')
    print('    ' + collection_hostname)


    print('OK STILL HERE')


# still here


export_definitions = eval(marcout_content)

if verbose:
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

jsonobj = json.loads(export_record_content)

if verbose:
    print('JSON parsed successfully.')

    print
    print('BLOCKS:')
    for key in export_definitions:
        print(key)

parameters_structure = export_definitions['known_parameters']
extracts_structure = export_definitions['json_extracted_properties']
functions_structure = export_definitions['functions']


export_content = compute_extracts(extracts_structure, jsonobj)

if verbose:
    print('-------------------------------------------------------')
print(export_content)
