#!/usr/bin/python

# work to get a minimal parser

expr = "'online resource (1 audio file (' + total_play_length(album_tracks) + ')) ;'"

# tokenize: get quote blocks
tokenized = []
current_block = ''
current_quotechar = None
for char in expr:
    if current_quotechar:
        # we are in a quote block
        if char == current_quotechar:
            # done
            current_block += char
            tokenized.append(current_block)
            # set up quoted block going forward
            current_block = ''
            current_quotechar = None
        else:
            # keep stashing
            current_block += char
    else:
        # we are not in a quoted block
        if char in '"\'':
            # starting a new quote block
            if current_block:
                # nonquoted content has been accumulated
                tokenized.append(current_block)
            # set up quoted block going forward
            current_quotechar = char
            current_block = char
        else:
            current_block += char


for block in tokenized:
    print block


