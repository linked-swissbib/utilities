__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '1.0'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Identifies distinct predicates in N-triples statements.
"""

predicate = set()
with open("/data/sbdump/ntriples_output/1/test.jsonld") as file:
    for f in file:
        predicate.add(f.split(" ")[1])
[print(p) for p in predicate]
