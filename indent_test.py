#!/usr/bin/python

def read_indent(line):
    indx = -1
    if not line.strip():
        return indx

    for char in line:
        indx += 1
        if char.strip():
            return indx

deflines = open('marcexport.define').readlines()

for line in deflines:
    print(line.rstrip())
    print(read_indent(line))