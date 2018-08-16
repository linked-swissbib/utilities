#!/usr/bin/env python3 -B

"""
Search for records which contains a subfield t in datafield 700. Use the script with the path to the directory containing the gzipped MARC-XML files as only argument.
"""

import xml.etree.ElementTree
import gzip
from os import listdir
from os.path import isfile, join
from sys import argv

PATH = argv[1]
FILENAMES = [join(PATH, f) for f in listdir(PATH) if isfile(join(PATH, f))]

rcounter = 0
fcounter = 0
for filename in FILENAMES:
    fcounter += 1
    readingmsg = 'Reading file no {}/{} (Results found until now: {})'.format(fcounter, len(FILENAMES), rcounter)
    print(readingmsg, end='\r')
    f = gzip.open(filename)
    parent = xml.etree.ElementTree.parse(f).getroot()
    for child in parent.getchildren():
        for grandchild in child.getchildren():
            if '700' in grandchild.attrib.values():
                for grandgrandchild in grandchild.getchildren():
                    if 't' in grandgrandchild.attrib.values():
                        rcounter += 1
                        readingmsg = 'Reading file no {}/{} (Results found until now: {})'.format(fcounter, len(FILENAMES), rcounter)
                        print(readingmsg, end='\r')
print(rcounter)
