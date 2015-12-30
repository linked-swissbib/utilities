import os
import fnmatch
import re
import gzip
import sys

__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Counts identifiers in Bulk API compliant gzipped JSON documents and collects them in a file named identifiers.csv.gz.
Takes one argument, the path to the directory where the files are stored.
"""


def addvalue(v, d):
    if v in d:
        d[v] += 1
    else:
        d[v] = 1


dirname = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.realpath("__file__"))
p1 = re.compile(b'"_id":"(.*?)"')
words = dict()

print("Creating file list")
filelist = []
for root, dirnames, filenames in os.walk(dirname):
    for filename in fnmatch.filter(filenames, '*.jsonld.gz'):
        filelist.append(os.path.join(root, filename))

fllen = str(len(filelist))
i = 1
for f in filelist:
    fileno = "[" + str(i) + "/" + fllen + "] "
    i += 1
    print(fileno + "Handling " + f)
    with gzip.open(f) as file:
        for line in file:
            if p1.search(line):
                addvalue(p1.search(line).group(1).decode("utf-8"), words)

with gzip.open('identifiers.csv.gz', 'wb') as file:
    print("Sorting and writing " + str(len(words)) + " keys")
    for k in sorted(words):
        file.write(str.encode(k + ',' + str(words[k]) + '\n'))
