#!/usr/bin/python3

"""
Checks if there aren't any dead links between __bibliographic resources__ and __person_ or __organisation__ entities respectively. Takes the path to file directory as only paramenter. Outputs information on STDERR, dead links on STDOUT.
"""

from sys import argv, stderr
from os import listdir
from os.path import isfile, join
import json


def compressid(identifier):
    splitted = identifier.split('/')
    entity = splitted[3][0]
    return entity + '/' + splitted[4]


def getids(filename, fieldname):
    with open(filename) as f:
        if fieldname == '@id':
            return set([compressid(obj[fieldname]) for obj in json.load(f) if fieldname in obj])
        else:
            return set([compressid(val) for obj in json.load(f) for val in obj[fieldname] if fieldname in obj])


PATH = argv[1]
FILENAMES = [join(PATH, f) for f in listdir(PATH) if isfile(join(PATH, f))]

BIBIDS = set()
ORGPERSIDS = set()
i = 0

for filename in FILENAMES:
    i = i + 1
    if 'bibliographicResource' in filename:
        print("({}/{}) {}".format(i, len(FILENAMES), filename), file=stderr)
        BIBIDS |= getids(filename, 'dct:contributor')
    elif 'organisation' in filename:
        print("({}/{}) {}".format(i, len(FILENAMES), filename), file=stderr)
        ORGPERSIDS |= getids(filename, '@id')
    elif 'person' in filename:
        print("({}/{}) {}".format(i, len(FILENAMES), filename), file=stderr)
        ORGPERSIDS |= getids(filename, '@id')

print("Comparing BIBIDS against ORGPERSIDS...", file=stderr)
BIBIDSDIFF = BIBIDS.difference(ORGPERSIDS)
print('\n'.join(BIBIDSDIFF))
print("{} orphans found".format(len(BIBIDSDIFF)), file=stderr)
print('\n')
print("Comparing ORGPERSIDS against BIBIDS...", file=stderr)
ORGPERSIDSDIFF = ORGPERSIDS.difference(BIBIDS)
print('\n'.join(ORGPERSIDSDIFF))
print("{} orphans found".format(len(ORGPERSIDSDIFF)), file=stderr)
