#!/usr/bin/python3

"""
Checks if two JSON objects with same @id-field are identical. The script takes two parameter, namly the paths to the directories of the files to be compared.
"""

import json
import sys
from os import listdir
from os.path import isfile, join
from random import sample


def getfiles(path):
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]


FILES1 = getfiles(sys.argv[1])
FILES2 = getfiles(sys.argv[2])


def generateindex(files):
    ind = dict()
    for sf in files:
        tempdict = dict()
        with open(sf) as f1:
            for obj in json.load(f1):
                tempdict[obj['@id']] = sf
        ind.update(tempdict)
    return ind


def searchid(obj1, files):
    obj1id = obj1['@id']
    targetfile = index[obj1id]
    with open(targetfile) as f1:
        for obj2 in json.load(f1):
            if obj2['@id'] == obj1id:
                if obj1 == obj2:
                    print("True:  {}".format(obj1id))
                else:
                    print("\n")
                    print("False: {}".format(obj1id))
                    print("{}".format(obj1))
                    print("\n")
                    print("{}".format(obj2))
                    print("\n")


index = generateindex(FILES2)


for singlefile in FILES1:
    with open(singlefile) as f:
        j = json.load(f)
        selection = sample(j, 5)
        for s in selection:
            searchid(s, FILES2)
