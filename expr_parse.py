#!/usr/bin/python

# work to get a minimal parser





opaques = {'"': '"', "'": "'"}
nestables = {'(':')', '[':']', '{':'}'}

# what does current_delims look like?
# it's a sequence of deelims encountered so far in traversing a string expr

# for
# (upper("hello" + "goodbye") + lower("boing"))

# []                ''
# ['(']             '('
# ['(']             '(', 'upper'
# ['(', '(']        '(', 'upper', '('
# ['(', '(', '"']   '(', 'upper', '(', "hel...
# ['(', '(']        '(', 'upper', '(', "hello"
# ['(', '(']        '(', 'upper', '(', "hello", ' + '
#                   '(', 'upper', '(', "hello", ' + '
# ['(', '(', '"']   '(', 'upper', '(', "hello", ' + ', "goo...
# ['(', '(']        '(', 'upper', '(', "hello", ' + ', "goodbye"
# ['(']             '(', 'upper', '(', "hello", ' + ', "goodbye", ')'
# ['(']             '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + '
# ['(']             '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower'
# ['(', '(']        '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower', '('
# ['(', '(', '"']   '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower', '(', "boi..
# ['(', '(']        '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower', '(', "boing"
# ['(']             '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower', '(', "boing", ')'
#   FINISH
# []                '(', 'upper', '(', "hello", ' + ', "goodbye", ')', ' + ', 'lower', '(', "boing", ')', ')'





def closes_delim(delims, char):
    '''Returns True if char closes LAST value in delims'''
    if not delims:
        # already closed (empty)
        return False

    # the last character in a delim sequence is looking for its closure
    openchar = delims[-1]   

    if openchar in opaques:
        # we are in a string literal
        return (char == opaques[openchar])
    if openchar in nestables:
        # nestable expression
        return (char == nestables[openchar])
    else:
        raise Exception('How did `' + current_delims[-1] + '` get into delims???')


def opens_delim(delims, char):
    if delims and delims[-1] in opaques:
        # this is what "opaque" means. a quoted literal can contain anything
        return False
    else:
        return char in opaques or char in nestables


opaques = {'"': '"', "'": "'"}
nestables = {'(':')', '[':']', '{':'}'}


def sweep(expr):
    # essentially a tokenizing pass
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
                top_blocks.append(current_block)

            elif char in nestables.values():
                top_blocks.append(current_block)
                # closing char gets its own block
                top_blocks.append(char)

            # reset
            current_block = ''
            current_delims.pop()

        elif opens_delim(current_delims, char):

            if char in nestables:
                if current_block:
                    top_blocks.append(current_block)
                # it gets its own block
                top_blocks.append(char)
                # reset
                current_block = ''
                current_delims.append(char)

            elif char in opaques:
                if current_block:
                    top_blocks.append(current_block)

                # put the char at the lead of the new block
                current_block = ''
                current_block += char
                current_delims.append(char)

        elif char == '+':
            # give this a block of its own, but make no delim entry
            # because this is an operator
            if current_block:
                top_blocks.append(current_block)
            top_blocks.append(char)
            current_block = ''

        else:
            # neither opens nor closes
            current_block += char

    # flush accumulated content to return value
    if current_block:
        top_blocks.append(current_block)
    return top_blocks


expr1 = "'online resource (1 audio file (' + total_play_length(album_tracks) + ')) ;'"

print
blocks = sweep(expr1)
restore = ''
for block in blocks:
    print(block)
    restore += block
print(restore)

print
expr2 = '"hello" + func1(func2(func3(main_artist_name))) + "goodbye"'
blocks = sweep(expr2)
restore = ''
for block in blocks:
    print(block)
    restore += block
print(restore)
