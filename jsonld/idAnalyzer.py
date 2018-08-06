import re
import gzip
import sys
import os

__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Counts numbers of identifiers in a file created by idCounter.py. Takes one argument, the path to the file.
"""


pbiblio = re.compile(b'http://data.swissbib.ch/resource/.{9},')
pdocu = re.compile(b'http://data.swissbib.ch/resource/.{9}/about"')
pperson = re.compile(b'http://data.swissbib.ch/person/')
porga = re.compile(b'http://data.swissbib.ch/organisation/')
pwork = re.compile(b'http://data.swissbib.ch/work/')

number = re.compile(b'[0-9]+$')

countUnique = {
    'bibliographicResource': 0,
    'document': 0,
    'person': 0,
    'organisation': 0,
    'work': 0
}

countTotal = {
    'bibliographicResource': 0,
    'document': 0,
    'person': 0,
    'organisation': 0,
    'work': 0
}


def iterator(filename):
    with gzip.open(filename) as file:
        for l in file:
            if pbiblio.match(l):
                countUnique['bibliographicResource'] += 1
                countTotal['bibliographicResource'] += int(number.search(l).group())
            elif pdocu.match(l):
                countUnique['document'] += 1
                countTotal['document'] += int(number.search(l).group())
            elif pperson.match(l):
                countUnique['person'] += 1
                countTotal['person'] += int(number.search(l).group())
            elif porga.match(l):
                countUnique['organisation'] += 1
                countTotal['organisation'] += int(number.search(l).group())
            elif pwork.match(l):
                countUnique['work'] += 1
                countTotal['work'] += int(number.search(l).group())

    print("""
    Type:                   Unique documents:\tTotal documents:\tRatio:
    bibliographicResource   {0:<17}\t{1:<16}\t{2:<6.1f}
    document                {3:<17}\t{4:<16}\t{5:<6.1f}
    person                  {6:<17}\t{7:<16}\t{8:<6.1f}
    organisation            {9:<17}\t{10:<16}\t{11:<6.1f}
    work                    {12:<17}\t{13:<16}\t{14:<6.1f}
    """.format(countUnique['bibliographicResource'], countTotal['bibliographicResource'],
               countUnique['bibliographicResource']/(1 if countTotal['bibliographicResource'] == 0 else countTotal['bibliographicResource'])*100,
               countUnique['document'], countTotal['document'],
               countUnique['document']/(1 if countTotal['document'] == 0 else countTotal['document'])*100,
               countUnique['person'], countTotal['person'],
               countUnique['person']/(1 if countTotal['person'] == 0 else countTotal['person'])*100,
               countUnique['organisation'], countTotal['organisation'],
               countUnique['organisation']/(1 if countTotal['organisation'] == 0 else countTotal['organisation'])*100,
               countUnique['work'], countTotal['work'],
               countUnique['work']/(1 if countTotal['work'] == 0 else countTotal['work'])*100))


iterator(str(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.realpath("__file__")))
