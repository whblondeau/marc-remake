#!/usr/bin/python


# Constants for subfield expression parse operations
opaque_delims = {'"': '"', "'": "'"}
nestable_delims = {'(':')', '[':']', '{':'}'}

import copy



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
            # because this is a unary operator
            append_normalized_block(current_block, top_blocks)
            # normalize whitespace for unary
            top_blocks.append(' + ')
            current_block = ''

        else:
            # non-delim, non-operator: content only:
            # neither opens nor closes
            current_block += char

    # flush accumulated content to return value
    append_normalized_block(current_block, top_blocks)

    return top_blocks






expr = "'online resource (1 audio file (' +  total_play_length (  album_tracks ) + ')) ;'"



blox = tokenize(expr)

print
for block in blox:
    print('`' + block + '`')

print
print(expr)
print('-----------------')
print(''.join(blox))
