__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

'''
Installs needed Python modules for script rdfxml2es.py and mapgen.py
'''

from sys import version_info
import pip


if int(version_info[0]) < 3:
    exit('Python version must be >= 3.0')

pkglist = (
    'rdflib',
    'rdflib-jsonld',
    'jsmin',
    'https://github.com/sschuepbach/pyld/zipball/master',
    'elasticsearch',
    'elasticsearch-dsl'
)
for info in map(lambda x: pip.main(['install', x]), pkglist):
    print(info)