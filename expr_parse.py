#!/usr/bin/python

# work to get a minimal parser: separate string literals 
# from evaluable expressions

# test stubs:

extracts = {
    'album_tracks': 'abcdef',
    'main_artist_name': 'prisxcilla yo'
}

def total_play_length(thang):
    return str(thang).upper()

def func1(onethang):

    return onethang.split('x') 

def func2(twothang):
    twothang[0] = twothang[0].upper()

def func3(threethang):
    return ':'.join(threethang)



def cut_into_segments(expr, literal_delims):
    top_blocks = []
    current_delim = None
    current_block = ''
    

    for char in expr:

        if current_delim:
            # we are in a string literal
            current_block += char
            if char == current_delim:
                # it's finished.
                top_blocks.append(current_block)
                current_delim = None
                current_block = ''
        else:
            # we are not in a string literal
            if char in literal_delims:
                #now we are starting one
                if current_block:
                    # stash
                    top_blocks.append(current_block)
                # initialize new literal block
                current_delim = char
                current_block = char
            else:
                current_block += char

    return top_blocks


def parse(expr, literal_delims = ('"', "'")):

    expr_list = cut_into_segments(expr, literal_delims)

    for block in expr_list:
        if not block:
            print('wtf')
            continue
        if block[0] in literal_delims:
            # string literal block
            print(block)
        else:
            # evaluable
            print(block)
            block = map(str.strip, block.split('+'))
            print(block)
            for subblock in block:
                if not subblock:
                    continue
                for key in extracts:
                    if key in subblock:
                        subblock = subblock.replace(key, "'" + extracts[key] + "'")
                print(subblock)
                print('EVAL:')
                print("'" + eval(subblock) + "'")








expr1 = "'online resource (1 audio file (' + total_play_length(album_tracks) + ')) ;'"

print
print parse(expr1)


expr2 = '"hello" + func1(func2(func3(main_artist_name))) + "goodbye"'
print
print parse(expr2)


print