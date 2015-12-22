__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '1.0'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Very simple tool to filter out only required DBPedia-properties.
"""

allowedProperties = [
    'http://dbpedia.org/ontology/abstract',
    'http://dbpedia.org/ontology/birthPlace',
    'http://dbpedia.org/ontology/deathPlace',
    'http://dbpedia.org/ontology/genre',
    'http://dbpedia.org/ontology/movement',
    'http://dbpedia.org/ontology/nationality',
    'http://dbpedia.org/ontology/notableWork',
    'http://dbpedia.org/ontology/occupation',
    'http://dbpedia.org/ontology/thumbnail',
    'http://dbpedia.org/ontology/influencedBy',
    'http://dbpedia.org/ontology/occupation',
    'http://dbpedia.org/ontology/partner',
    'http://dbpedia.org/ontology/pseudonym',
    'http://dbpedia.org/ontology/spouse',
    'http://dbpedia.org/ontology/alternativeNames',
    'http://dbpedia.org/ontology/author',
    'http://dbpedia.org/ontology/influenced',
    'http://dbpedia.org/ontology/deathYear',
    'http://dbpedia.org/ontology/birthYear',
]

with open('/data/sbdump/test_output.nt', 'w') as t:
    with open('/data/sbdump/test.nt', 'r') as f:
        for l in f:
            property = l.split("> <")[1]
            if property.startswith('http://dbpedia.org/ontology'):
                cleaned_property = property.split(' ')[0]
                if cleaned_property.endswith('>'):
                    cleaned_property = cleaned_property[:-1]
                if cleaned_property not in allowedProperties:
                    continue
            t.write(l)
