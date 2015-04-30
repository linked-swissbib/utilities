__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

import elasticsearch_dsl as dsl
from pprint import pprint
import argparse


def mapping(estype, ofile):
    """
    Creates the mapping for Elasticsearch
    :param estype: Name of ES type
    :param ofile: Name of file where the mapping will be stored
    """
    # TODO: Set properties for mapping
    m = dsl.Mapping(estype)
    # Adding JSON-LD context
    context = dsl.Object()
    namespaces = ['bibo', 'dbp', 'dc', 'dct', 'foaf', 'rdau', 'rdf', 'rdfs', 'skos']
    for token in namespaces:
        context = context.property(token, 'string', index='no')
    m = m.field('@context', context)
    # Adding JSON-LD graph fields
    m = m.field('@id', 'string', index='not_analyzed')
    m = m.field('@type', 'string', index='not_analyzed')
    m = m.field('dct:bibliographicCitation', 'string', index='analyzed', analyzer='standard')
    m = m.field('rdau:contentType', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('dc:contributor', 'string', index='analyzed')
    m = m.field('dct:contributor', 'string', index='analyzed')
    m = m.field('bibo:edition', 'string', index='analyzed')
    m = m.field('dct:alternative', 'string', index='analyzed',
                fields={'folded': dsl.String(analyzer='text_folded')})
    m = m.field('dc:format', 'string', index='analyzed')
    m = m.field('dct:hasPart', 'string', index='analyzed')
    m = m.field('rdfs:isDefinedBy',
                dsl.Object().property('@id', 'string', index='analyzed', analyzer='extr_id'))
    m = m.field('bibo:isbn10', 'string', index='not_analyzed')
    m = m.field('bibo:isbn13', 'string', index='not_analyzed')
    m = m.field('dct:issued', 'string', index='analyzed')
    m = m.field('dct:language', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:mediaType', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:noteOnResource', 'string', index='not_analyzed')
    m = m.field('dct:alternative', 'string', index='analyzed',
                fields={'folded': dsl.String(analyzer='text_folded')})
    m = m.field('rdau:placeOfPublication', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('dct:title', 'string', index='analyzed',
                fields={'folded': dsl.String(analyzer='text_folded')})
    m = m.field('dct:isPartOf', dsl.Object().property('@id', 'string', index='not_analyzed'))
    # Save the mapping in ES
    of = open(ofile, mode='x')
    pprint(m.to_dict(), stream=of)
    of.close()
    # m.save(esindex, using=escon)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Creates the mapping for Elasticsearch")
    parser.add_argument('type', metavar='<name>', type=str, help='Name of ES type')
    parser.add_argument('outputfile', metavar='<file>', type=str, help='Output file')
    args = parser.parse_args()

    mapping(args.type, args.outputfile)