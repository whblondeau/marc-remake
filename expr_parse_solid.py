#!/usr/bin/python

# work to get a minimal parser

def closes_current_delims(current_delims, opaques, nestables, char):
    '''Returns truth value if char closes first value
    in current_delims'''
    if not current_delims:
        return False
    if current_delims[0] in opaques:
        # we are in a string literal
        return (char == opaques[current_delims[0]])
    if current_delims[0] in nestables:
        # nestable expression
        return (char == nestables[current_delims[0]])
    else:
        raise Exception('How did `' + current_delims[0] + '` get into current_delims???')





def sweep(expr):
    top_blocks = []     # sequence of delimited blocks and non-delimited blocks
    current_block = ''
    current_delims = []

    # startstop_pairs... 
    # opaque block - ':' or ":", then
    # nestables (:)[:]{:}
    opaques = {'"': '"', "'": "'"}
    nestables = {'(':')', '[':']', '{':'}'}

    for char in expr:
        if current_delims:
            # we are in a delimited block, awaiting closure
            if closes_current_delims(current_delims, opaques, nestables, char):
                # we are matching an earlier opening. If quote, no thing.
                # if nestable... a little more involved.
                current_block += char

                if char in nestables.values():
                    nested_
                    # work backwards for matching startchar
                    for key in nestables.keys():
                        if key in current_block[1:-1]:
                            print('got a nested hit: ' + key)
                            nested = True
                            
                    if nested:
                        top_blocks.append(current_block[0])
                        print('about to recurse on ')
                        children = sweep(current_block[1:-1])
                        top_blocks.extend(children)
                        top_blocks.append(current_block[-1])
                    else:
                        top_blocks.append(current_block)
                else:
                    # leaving an opaque (i.e., string literal) block
                    top_blocks.append(current_block)

                    # set up nondelimited block going forward
                    current_block = ''
                    current_delims = []
            else:
                # keep stashing
                current_block += char
        else:
            # we are not in a delimited block
            if char in opaques:
                if current_block:
                    # stash it
                    top_blocks.append(current_block)
                # reinitialize
                current_block = char
                current_startchar = char
                current_stopchar = opaques[char]

            elif char in nestables:
                if current_block:
                    # stash it
                    top_blocks.append(current_block)
                # reinitialize
                current_block = char
                current_startchar = char
                current_stopchar = nestables[char]
                current_nesting_delims = [char]

            else:
                current_block += char

    return top_blocks

expr1 = "'online resource (1 audio file (' + total_play_length(album_tracks) + ')) ;'"

print
for block in sweep(expr1):
    print(block)

expr2 = '"hello" + func1(func2(func3(main_artist_name))) + "goodbye"'
print
for block in sweep(expr2):
    print(block)

print
