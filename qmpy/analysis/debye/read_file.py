#!/usr/bin/python
#read_file v1.0 5-3-2011 Jeff Doak jwd686@u.northwestern.edu
import sys

#Module to read in a space-delineated file of arbitrary size.

def read_file(filename,type="",transpose=False,sep=None,quiet=False,delr=None,
        delc=None):
    """Function to read in a space-delineated file of arbitrary size."""
    # Helper functions for a switch-like statement.
    def _default(line):
        return line
    def _string(line):
        temp = str(line)
        return temp
    def _float(line):
        temp = float(line)
        return temp
    def _integer(line):
        temp = int(line)
        return temp
    
    # Dictionary for performing switch-like statement.
    case = { "" : _default,
            "str" : _string,
            "float" : _float,
            "int" : _integer,
    }
    try:
        file = open(filename,'r')
    except IOError:
        if quiet is True:
            return []
        else:
            raise
    # Read in the file one line at a time, appending each sep delineated entry
    # to the list contents.
    contents = []
    i = 0
    for line in file:
        contents.append([])
        line = line.split(sep)
        for j in range(len(line)):
            try:
                contents[i].append(case[type](line[j]))
            except (KeyError,ValueError):
                contents[i].append(_default(line[j]))
        i += 1
    file.close()
    # Transpose the array before returning it, if desired.
    if transpose is True:
        temp = []
        for j in range(len(contents[0])):
            temp.append([])
            for i in range(len(contents)):
                try:
                    temp[j].append(contents[i][j])
                except IndexError:
                    temp[j].append("")
        contents = temp
    return contents

def main(argv):
    flag = 0
    filename = argv[1]
    if len(argv) > 2:
        type = argv[2]
    else:
        contents = read_file(filename)
        flag = 1
    if len(argv) > 3:
        transpose = argv[3]
        if transpose == "True":
            transpose = True
    elif flag == 0:
        contents = read_file(filename,type)
        flag = 1
    if len(argv) > 4:
        quiet = argv[4]
        if quiet == "True":
            quiet = True
    elif flag == 0:
        contents = read_file(filename,type,transpose)
        flag = 1
    if flag == 0:
        contents = read_file(filename,type,transpose,quiet)
    return contents

if __name__ == "__main__":
    contents = main(sys.argv)
    print contents
