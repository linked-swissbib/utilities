from lxml import etree
from sys import argv
from os import listdir
from os.path import isfile, join

__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2016, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '1.0'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Extracts values from marc field 035.
"""

files = [f for f in listdir(argv[1]) if isfile(join(argv[1], f))]
codes = []
for f in files:
    tree = etree.parse(f)
    lsys = tree.xpath("//ns:datafield[@tag='035']/ns:subfield[@code='a']",
                      namespaces={'ns': 'http://www.loc.gov/MARC21/slim'})
    codes.extend([c.text for c in lsys])
for c in codes:
    print(c)
