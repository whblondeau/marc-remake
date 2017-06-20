#!/usr/bin/python

# work to get a minimal parser

def sweep(expr):
    top_blocks = []     # sequence of delimited blocks and non-delimited blocks
    current_block = ''
    current_startchar = None
    current_stopchar = None
    current_nesting_delims = None

    # startstop_pairs... 
    # opaque block - ':' or ":", then
    # nestables (:)[:]{:}
    opaques = {'"': '"', "'": "'"}
    nestables = {'(':')', '[':']', '{':'}'}

    for char in expr:
        if current_stopchar:
            # we are in a delimited block, awaiting closure
            if char == current_stopchar:
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
                    # leaving 
                    top_blocks.append(current_block)

                # set up nondelimited block going forward
                current_block = ''
                current_startchar = None
                current_stopchar = None
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


# # tokenize: get quote blocks
# tokenized = []
# current_block = ''
# current_quotechar = None
# for char in expr:
#     if current_quotechar:
#         # we are in a quote block
#         if char == current_quotechar:
#             # done
#             current_block += char
#             tokenized.append(current_block)
#             # set up quoted block going forward
#             current_block = ''
#             current_quotechar = None
#         else:
#             # keep stashing
#             current_block += char
#     else:
#         # we are not in a quoted block
#         if char in '"\'':
#             # starting a new quote block
#             if current_block:
#                 # nonquoted content has been accumulated
#                 tokenized.append(current_block)
#             # set up quoted block going forward
#             current_quotechar = char
#             current_block = char
#         else:
#             current_block += char



    


