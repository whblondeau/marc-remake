#!/usr/bin/python

def value_after_first(expr, split_expr):
    '''This function prevents collision between differing usages of
    demarcators (":" in the current implementation)
    '''
    return split_expr.join(expr.split(split_expr)[1:]).strip()


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
        - 'json_extracted_properties', named expressions for pulling values from a
            JSON instance.
        - 'marc_field_templates', an ordered sequence of data structures listing
            desired fixed values, and album JSON extraction expressions, for MARC
            fields.
            This list of templates thus controls field order, subfield order,
            and instructions for pulling data from the expected JSON instance.

    This marcexport datastructures dictionary/map/hash/object is returned.
    '''
    defblocks = {}
    parse_order = []
    current_blockname = None

    for line in deflines:
        if line.strip().endswith('--------'):
            line = line.strip()
            current_blockname = line[:line.find('----')]
            current_blockname = current_blockname.lower().replace(' ', '_')
            defblocks[current_blockname] = []
            parse_order.append(current_blockname)

        else:
            if current_blockname:
                defblocks[current_blockname].append(line.strip())

    # print(str(len(defblocks)) + ' blocks read in.')
    # for block in defblocks:
    #     print(block + ' (' + str(len(defblocks[block])) + ' lines)')
    # print

    # now evaluate marcexport define DATASTRUCTURE content as required
    marcdefs = {}
    marcdefs['parse_order'] = parse_order


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
        if not line:
            continue

        # extract the function name
        funcname = line.split('(')[0]
        marcdefs['functions'][funcname] = line


    # EXTRACTORS:
    # expressions for pulling data out of JSON instances
    marcdefs['json_extracted_properties'] = {}
    for line in defblocks['json_extracted_properties']:
        line = line.strip()
        if not line:
            continue

        parts = line.split('=')
        # someone might put some equals signs in the expr - condition or something
        marcdefs['json_extracted_properties'][parts[0].strip()] = ('='.join(parts[1:])).strip()


    # TEMPLATES: 
    # ordered sequence of templates for MARC fields
    marcdefs['marc_field_templates'] = None

    field_data = [] # list of MARC field data assembled according to definitions
    current_field = None

    # using a while loop to have control over indx for readaheads
    indx = -1
    while indx < len(defblocks['marc_field_templates']) - 1:

        indx += 1
        line = defblocks['marc_field_templates'][indx]

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
            current_field['foreach']['eachitem'] = foreachexpr[0].strip()
            current_field['foreach']['itemsource'] = foreachexpr[1].strip()

        elif line.startswith('EACH-SUBFIELD:'):
            if 'subfields' not in current_field['foreach']:
                current_field['foreach']['subfields'] = []
            eachsub_code = line.split(':')[1].strip()
            eachsub_expr = defblocks['marc_field_templates'][indx + 1].strip()
            current_field['foreach']['subfields'].append({eachsub_code: eachsub_expr})

        elif line.startswith('SORT BY:'):
            # we may one day want to support "sort by a, b" expressions...
            # so make this an array, also
            if 'sortby' not in current_field['foreach']:
                current_field['foreach']['sortby'] = []
            sortby_expr = value_after_first(line, ':')
            current_field['foreach']['sortby'].append(sortby_expr)

        elif line.startswith('DEMARC WITH:'):
            demarc_expr = value_after_first(line, ':')
            current_field['foreach']['demarcator'] = demarc_expr

        elif line.startswith('TERMINATE SUBFIELDS WITH:'):
            terminator_expr = value_after_first(line, ':')
            current_field['foreach']['terminator'] = terminator_expr

        # we do not want to grab subfields that are within a 
        elif line.startswith('SUBFIELD:'):
            if 'subfields' not in current_field:
                current_field['subfields'] = []
            subfield_code = line.split(':')[1].strip()
            subfield_expr = defblocks['marc_field_templates'][indx + 1].strip()
            current_field['subfields'].append({subfield_code: subfield_expr})

    marcdefs['marc_field_templates'] = field_data

    return marcdefs


def pretty_print_struct(context_blockname, item, indent, ind_str='  '):
    retval = ''
    if item:
        if isinstance(item, list):
            for child in item:
                retval += '\n'
                retval += (pretty_print_struct(context_blockname, child, indent + 1, ind_str))

        elif isinstance(item, dict):

            keyset = item.keys()

            # put field templates in human-friendly order
            if context_blockname == 'marc_field_templates':
                keyset = ['tag', 'indicator_1', 'indicator_2']
                keyset = keyset + [key for key in item.keys() if key not in keyset]

            for key in keyset:
                retval += '\n'
                retval += (str(key)) + ' ' + str(item[key])

        else:
                retval += (ind_str * indent + str(item).strip()) 

    return retval + '\n'


import sys
import copy

if '--help' in sys.argv:
    print(usage)
    exit(0)

call_options = [arg for arg in sys.argv[1:] if arg.startswith('-')]
call_params = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

marcout_filename = call_params[0]

verbose = '--verbose' in call_options

srcfile = open(marcout_filename)
srclines = srcfile.readlines()
srcfile.close()

if verbose:
    print('MARCout file "' + marcout_filename + '" opened and read.')

# blocknames preserves parse order
marcout_structures = parse_marcexport_deflines(srclines)

if verbose:
    print('MARCout file "' + marcout_filename + '" parsed.')

if verbose:
    for blockname in marcout_structures['parse_order']:
        print
        print(blockname.upper())
        if blockname in marcout_structures:
            print(pretty_print_struct(blockname, marcout_structures[blockname], 0))
            print
            print('--------')
            print

else:
    print(marcout_structures)