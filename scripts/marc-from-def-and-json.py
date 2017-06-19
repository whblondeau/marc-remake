#!/usr/bin/python
# so "/" vs "//" integer division will behave the same 
# in python 2 and 3.
# imports from __future__ must be at the head of the file,
# which is why this is here.
from __future__ import division


def extract_defined_properties(jsonobj, extractlines):
    '''`jsonobj` is a JSON album record (logically the same as "album_json"
    in marcexport.define).
    `extractlines` is the content of the "JSON EXTRACTED PROPERTIES" block
    in marcexport.define. Blank lines are not necessarily removed.
    Returns a hash of properties, named according to the instructions
    found in the block.
    '''
    album_json = jsonobj
    retval = {}
    for line in extractlines:
        line = line.strip()
        if not line:
            continue
        if '=' in line:
            propname, expr = map(str.strip, line.split('='))
            retval[propname] = eval(expr)
    return retval

def assemble_export_field_info(exportfieldlines, extracted_properties):

    field_data = [] # list of MARC field data assembled accfording to definitions
    current_field = None
    for indx, line in enumerate(exportfieldlines):
        line = line.rstrip()
        strippedline = line.strip()
        if line.endswith('----'):
            continue

        if not strippedline:
            # blank line --> field is done
            if current_field:
                field_data.append(current_field)
                current_field = None

        if strippedline.startswith('FIELD:'):
            # new field
            current_field = {}
            fieldtag = strippedline.split(':')[1].strip()
            current_field['tag'] = fieldtag

        elif strippedline.startswith('INDC1:'):
            indc1 = strippedline.split(':')[1].strip()
            if indc1 == 'blank':
                indc1 = ' '
            current_field['indc1'] = indc1

        elif strippedline.startswith('INDC2:'):
            indc2 = strippedline.split(':')[1].strip()
            if indc2 == 'blank':
                indc2 = ' '
            current_field['indc2'] = indc2

        elif strippedline.startswith('SUBFIELD:'):
            if 'subfields' not in current_field:
                current_field['subfields'] = []
            subfield_code = strippedline.split(':')[1].strip()
            subfield_content = exportfieldlines[indx + 1].strip()
            subfield_content = compute_subfield_val(subfield_content, extracted_properties)
            current_field['subfields'].append({subfield_code: subfield_content})

    return field_data


def biblio_name(main_artist_name):
    pass

def release_year(release_date):
    pass

def release_decade(release_date):
    pass

def marc_field_from_values(jsonobj, field_pattern):
    '''This function, following the field pattern from the
    marcexport.define file, constructs the abstract (e.g. dict)
    representation of MARC data.
    '''
    content = {}
    in_subfield = None
    for line in field_pattern:
        if line.strip().startswith('FIELD:'):
            in_subfield = None
            content['tag'] = line.split(':')[1].strip()
        elif line.strip().startswith('INDC1:'):
            content['indicator_1'] = line.split(':')[1].strip()
        elif line.strip().startswith('INDC2:'):
            content['indicator_2'] = line.split(':')[1].strip()




def abstract_tracks(tracks, subfield_pattern, demarcator):
    '''from a JSON `tracks` node, assembles the MARC subfields list of 
    individual track subfileds in order
    '''

    for track in tracks:
        pass


# def render_tracks():
#     trackrenders = {}   # trackrender:position

#     for track in tracks:
    


# accepts a comma separated list in string form, and a boolean
# that, if set to true, will stipulate use of the Oxford comma.
# Returns the list with leading and trailing whitespace stripped from 
# list items, separated by commas, with " and " inserted in lieu of
# the final separator.
def pretty_comma_list(listexpr, oxford=False):

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

    # print('hours: ' + str(hours))
    # print('minutes: ' + str(minutes))
    # print('seconds:' + str(seconds))

    # print('zeropad(minutes, 2): ' + zeropad(str(minutes), 2))
    # print('zeropad(seconds, 2): ' + zeropad(str(seconds), 2))

    retval = ':' + zeropad(str(seconds), 2)
    if minutes:
        if hours:
            retval = ':' + zeropad(str(minutes), 2) + retval
        else:
            retval = str(minutes) + retval
    if hours:
        retval = str(hours) + ':' + retval

    return retval

def compute_subfield_val(expr, extracts):
    retval = expr

    stack = []
    # do we have parens? is this a concatenation? bozhe moi.
    accum = ''
    for char in expr:
        if char in '(+':
            # new stack entry
            stack.append(accum)
            accum = char
        elif char == ')':
            stack.append





    for key in extracts:
        if key in expr: 
            expr = expr.replace(key, '"' + str(extracts[key]) + '"')
        try:
            retval = eval(expr)
        except Exception as e:
            print(e)
        
    return retval


def render_duration(duration_in_float_seconds):
    return '(' + h_m_s(duration_in_float_seconds) + ')'


def total_play_length(tracks):

    float_seconds = 0.0
    for track in tracks:
        float_seconds += track['duration']
    
    return h_m_s(float_seconds)


def scan_marcexport_lines(marclines):

    marcfield_defs = []
    block_indxs = {}
    cur_block = None
    for indx, line in enumerate(marclines):
        if line.strip().endswith('--------'):
            line = line.strip()
            blockname = line[:line.find('----')]

            if cur_block:
                # close out old block
                block_indxs[cur_block].append(indx-1)

            # start new block
            cur_block = blockname
            block_indxs[blockname] = []
            block_indxs[blockname].append(indx)

    block_indxs[cur_block].append(len(marclines) - 1)

    return block_indxs




define_blocks = {}

extracted_properties = {}




usage = '''
USAGE: marc-from-def-and-json <marc def file> <json_file> <collection name> <collection host>
'''

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

# still here
marclines = None
with open(def_filename) as marcdef_file: 
    marclines = marcdef_file.readlines()
    marcdef_file.close()

jsonsource = None
with open(json_filename) as json_file:
    jsonsource = json_file.read()
    json_file.close()

jsonobj = json.loads(jsonsource)

print('JSON parsed successfully.')


# testdurs = [
#     364.61401360544215,
#     400.06068027210887,
#     308.56820861678005,
#     509.6957823129252,
# ]

# print
# print('Testing durations:')
# for dur in testdurs:
#     print(dur)
#     print(h_m_s(dur))

# print
# print('Testing album duration:')
# tracks = jsonobj['album']['tracks'] 
# print(type(tracks))

# print('total_play_length(tracks)' + str(total_play_length(tracks)))

define_indxs = scan_marcexport_lines(marclines)
print
print('define_indexs:')
print(define_indxs)

# define_blocks is source text from the marcexport.define file
define_blocks = {}
for block in define_indxs:
    print(block)
    print(define_indxs[block])
    startswith = define_indxs[block][0]
    endsbefore = define_indxs[block][1]
    define_blocks[block] = marclines[startswith:endsbefore]

# for blockname in define_blocks:
#     print
#     print(blockname)
#     for line in define_blocks[blockname]:
#         print(line.rstrip())
#     print

# extract properties from JSON
extractlines = define_blocks['JSON EXTRACTED PROPERTIES']
extracted_properties = extract_defined_properties(jsonobj, extractlines)
for prop in extracted_properties:
    print
    print(prop + ': ' + str(extracted_properties[prop]))

# marshal MARC record data
exportfieldlines = define_blocks['EXPORT DEFINE']
export_field_info = assemble_export_field_info(exportfieldlines, extracted_properties)

for field in export_field_info:
    print
    print(field)

