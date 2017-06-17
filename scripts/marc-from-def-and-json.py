#!/usr/bin/python


def biblio_name(main_artist_name):
    pass

def release_year(release_date):

def release_decade(release_date):

def render_track_duration(track_duration):

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


def total_play_length(tracks):

    hours = 0
    minutes = 0
    seconds = 0

    float_seconds = 0.0
    for track in tracks:
        float_seconds += track['duration']
    seconds = int(round(float_seconds))

    bucket_sizes = (
        (hours, 3600),    # 60 * 60
        (minutes, 60),
        (seconds, 1),
    )

    for bucket, count in intervals[:-1]:
        # floor division imported from __future__
        value = seconds // count
        if value:
            bucket += value
            seconds -= value * count





def parse_marcexport_lines(marclines):


    marcfield_defs = []
    for line in marclines:




usage = '''
USAGE: marc-from-def-and-json <marc def file> <json_file> <collection name> <collection host>
'''

import sys
import os, os.path
import json
import datetime
# so "/" vs "//" integer division will behave the same in python 2 and 3
from __future__ import division     

if '--help' in sys.argv:
    print(usage)
    exit(0)

call_options = [arg for arg in sys.argv[1:] if arg.startswith('-')]
call_params = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

def_filename, json_filename, collection, hostname = call_params[:4]

print('MARC export definition file:')
print('    ' + def_filename)
print('JSON sourcefile:')
print('    ' + json_filename)
print('Collection namespace:')
print('    ' + collection)
print('Hostname:')
print('    ' + hostname)

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

