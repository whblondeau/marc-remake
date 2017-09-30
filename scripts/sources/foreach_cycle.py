
# album_text = '{
#     "album": {
#         "id": "mischa-lively-album",
#         "asset_type": "album",
#         "title": "Pillow",
#         "round": "boombox-fall-2016",
#         "front_cover_art": "https://boombox-jsfs.library.nashville.org/complete-submission/albums/mischa-lively-album/1500x1500_300ppi_pillow_digi_ep_art_rgb.jpg",
#         "main_artist": "mischa-lively",
#         "main_artist_name": "Mischa Lively",
#         "release_date": "2016-05-20T00:00:00.000Z",
#         "record_label": "RACECAR",
#         "upc": null,
#         "genre": "Dance & Electronic",
#         "badge_image": null,
#         "badge_tag": null,
#         "spoken_languages": "English",
#         "auth_required_to_stream": false,
#         "tracks": [{
#             "title": "Held Open",
#             "filename": "4-Held Open.wav",
#             "url": "https://boombox-jsfs.library.nashville.org/complete-submission/mischa-lively-album/4-held-open--1474315403000.wav",
#             "position": 4,
#             "duration": 400.06068027210887,
#             "access_token": "cc7163c59ff3ae7501cfc65bb835165c5946c689"
#         }, {
#             "title": "A Posture For Learning",
#             "filename": "3-A Posture For Learning.wav",
#             "url": "https://boombox-jsfs.library.nashville.org/complete-submission/mischa-lively-album/3-a-posture-for-learning--1474315403000.wav",
#             "position": 3,
#             "duration": 364.61401360544215,
#             "access_token": "3e1d204b2707e3f4565b36a1ae12104c0ad3e5f2"
#         }, {
#             "title": "Blakeup",
#             "filename": "2-Blakeup.wav",
#             "url": "https://boombox-jsfs.library.nashville.org/complete-submission/mischa-lively-album/2-blakeup--1474315403000.wav",
#             "position": 2,
#             "duration": 308.56820861678005,
#             "access_token": "4278bff4e224f6cb8ea564a05f73631a483b622e"
#         }, {
#             "title": "Pillow",
#             "filename": "1-Pillow.wav",
#             "url": "https://boombox-jsfs.library.nashville.org/complete-submission/mischa-lively-album/1-pillow--1474315403000.wav",
#             "position": 1,
#             "duration": 509.6957823129252,
#             "access_token": "7e9440a2438e3435a91aafcdce034c2016b018ea"
#         }]
#     },
#     "owner": "be772e054e21d314f1a4ee9040308af6e1cb6609"
# }'


# Constants for subfield expression parse operations
opaque_delims = {'"': '"', "'": "'"}
nestable_delims = {'(':')', '[':']', '{':'}'}


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



# required functions
def normalize_date(dateval):
    if not dateval:
        return ''
    dateval = str(dateval)
    dateval = dateval.split('T')[0]
    return dateval


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
    atandard hours, minutes, seconds representation.
    '''
    return '(' + h_m_s(float(duration_in_float_seconds)) + ')'





import json

album_text = open('jsons/mischa-lively-album.json').read()

album_json = json.loads(album_text)


# EXPECTED PARAMETERS
# collection_name
# collection_host


# extracted properties
record_label = album_json['album']['record_label']
spoken_languages = album_json['album']['spoken_languages']
main_artist_name = album_json['album']['main_artist_name']
submission_round = album_json['album']['round']
album_id = album_json['album']['id']
album_tracks = album_json['album']['tracks']
release_date = normalize_date(album_json['album']['release_date'])
front_cover_art = album_json['album']['front_cover_art']

# artist_is_group = album_json['album']['artist_is_group']

genre = album_json['album']['genre']
album_title = album_json['album']['title']


album_foreach_track_def = {
    'tag': '505',
    'indicator_1': '0',
    'indicator_2': '0',
    'foreach': {
        'eachitem': 'track',
        'demarcator': ' --', 
        'subfields': 
            [
                {'t': 'track::title'},
                {'g': 'render_duration(track::duration)'}
            ],
        'itemsource': album_tracks, 
        'sortby': 
            [
                'track::position'
            ],
        'terminator': '.'
    }
}

def rewrite_for_context(marcout_expr, context_expr, context_varname):
    '''Translates context-identifying MARCout expression into an evaluable form.
    Parameters: `marcout_expr` is the MARCout expression.
    `context_expr` is the MARCout identifier for the context.
    `context_varname` is the evaluable variable reference for the context.
    EXAMPLE from FOREACH block:
    marcout_expr: 'render_duration(track::duration)'
    context_expr: 'track::'
    context_varname: 'current_item'
    return value: "render_duration(current_item['duration'])"
    '''
    tokens = tokenize(marcout_expr)
    for indx, token in enumerate(tokens):
        if token.startswith(context_expr):
            # change from MARCout notation to dict notation
            tokens[indx] = token.replace(context_expr, context_varname + '[\'') + '\']'
        # print(token)
    return ''.join(tokens)


def render_foreach(foreach_def_block):
    '''This function analyzes, sorts, and computes MARC subfield content that is defined
    in a MARCout FOREACH block, returning the subfield content properly rendered.

    '''
    retval = ''

    # local variables for notational clarity
    itemsource = foreach_def_block['itemsource'] # must match an evaluable variable
    eachitem_name = foreach_def_block['eachitem']
    eachitem_expr = eachitem_name + '::'
    demarc = foreach_def_block['demarcator']
    terminator = foreach_def_block['terminator']

    sortkeys = foreach_def_block['sortby']
    # TODO: deal with sortby for cascade if more than one sort key in this list
    sortkey = sortkeys[0].lstrip(eachitem_expr)

    subfield_defs = foreach_def_block['subfields']

    # sort the list being iterated
    # TODO: make a better sort function for cascading sort
    itemsource.sort(key=lambda x: x[sortkey])


    # append rendered and demarcated subfields to retval
    for eachitem in itemsource:
        rendered_subfields = ''

        # this respects subfield definition order
        for subfield_def in subfield_defs:

            # a subfield_def is a dict of form {subfield_code: evaluable expression}
            for subcode in subfield_def.keys():
                subfield_expr = subfield_def[subcode]

                print('  ' + subcode + ': ' + subfield_expr)

                subfield_expr = rewrite_for_context(subfield_expr, eachitem_expr, 'eachitem')
                print('  ' + subcode + ': ' + subfield_expr)
                print('  ' + subcode + ': ' + eval(subfield_expr))
                rendered_subfields += '$'
                rendered_subfields += subcode
                rendered_subfields += eval(subfield_expr)

        retval += rendered_subfields
        retval += demarc
    
        print(eachitem[sortkey])

        print


    return retval + terminator

print('calling render_foreach')
rendered = render_foreach(album_foreach_track_def['foreach'])

print('------------------')
print
print(rendered)
print
print('------------------')
print('ALL OK')
