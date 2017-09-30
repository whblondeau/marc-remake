

buf = ''
bytecount = 0
filename = '/Users/whb/Downloads/cock-and-swan-splurge-land'
filename = '/Users/whb/Downloads/doug-moser-and-jonathan-estes-album'
filename = '/Users/whb/rabble/marc-remake/simple'
with open(filename, 'rb') as srcfile:
    while True: 
        byte = srcfile.read(1)
        if not byte: break
        bytecount += 1
        buf += byte

print('buf')
print(str(bytecount))



