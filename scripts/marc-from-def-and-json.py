#!/usr/bin/python
# so "/" vs "//" integer division will behave the same in python 2 and 3
from __future__ import division


def biblio_name(main_artist_name):
    pass

def release_year(release_date):
    pass

def release_decade(release_date):
    pass

def render_tracks(tracks):
    trackrenders = {}   # trackrender:position
    


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


def render_duration(duration_in_float_seconds):
    return '(' + h_m_s(duration_in_float_seconds) + ')'


def total_play_length(tracks):

    float_seconds = 0.0
    for track in tracks:
        float_seconds += track['duration']
    
    return h_m_s(float_seconds)


def parse_marcexport_lines(marclines):

    tripwire = 0
    marcfield_defs = []
    for line in marclines:
        tripwire += 1




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


testdurs = [
    364.61401360544215,
    400.06068027210887,
    308.56820861678005,
    509.6957823129252,
]

print
print('Testing durations:')
for dur in testdurs:
    print(dur)
    print(h_m_s(dur))

print
print('Testing album duration:')
tracks = jsonobj['album']['tracks'] 
print(type(tracks))

print('total_play_length(tracks)' + str(total_play_length(tracks)))

