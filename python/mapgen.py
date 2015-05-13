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


def gencontext(mapobj):
    context = dsl.Object()
    namespaces = ['bibo', 'dbp', 'dc', 'dct', 'foaf', 'rdau', 'rdf', 'rdfs', 'skos', 'xsd']
    for token in namespaces:
        context = context.property(token, 'string', index='no')
    return mapobj.field('@context', context)


def genbibres(stream, estype='bibliographicResource'):
    """
    Creates the mapping for type bibliographicResource in Elasticsearch
    :param estype: Name of ES type (defaults to 'bibliographicResource')
    """
    m = dsl.Mapping(estype)
    # Set properties
    m.properties.dynamic = 'strict'
    # Adding mapping
    m = gencontext(m)
    m = m.field('@id', 'string', index='not_analyzed')
    m = m.field('@type', 'string', index='no')
    m = m.field('bibo:edition', 'string', index='analyzed')
    m = m.field('bibo:isbn10', 'string', index='not_analyzed')
    m = m.field('bibo:isbn13', 'string', index='not_analyzed')
    m = m.field('bibo:issn', 'string', index='not_analyzed')
    m = m.field('dbp:originalLanguage', dsl.Object().property('@id', 'string', index='not_analyzed'))
    contrib = dsl.Nested()
    contrib = contrib.property('@id', dsl.String(index='no'))
    contrib = contrib.property('@type', dsl.String(index='no'))
    contrib = contrib.property('dbp:birthYear', dsl.String(index='not_analyzed'))
    contrib = contrib.property('dbp:deathYear', dsl.String(index='not_analyzed'))
    contrib = contrib.property('foaf:firstName', dsl.String(index='analyzed'))
    contrib = contrib.property('foaf:lastName', dsl.String(index='analyzed'))
    contrib = contrib.property('foaf:name', dsl.String(index='analyzed'))
    contrib = contrib.property('rdfs:label', dsl.String(index='analyzed'))
    contrib = contrib.property('skos:note', dsl.String(index='analyzed'))
    m = m.field('dc:contributor', contrib)
    m = m.field('dc:format', 'string', index='analyzed')
    m = m.field('dct:alternative', 'string', index='analyzed', fields={'folded': dsl.String(analyzer='text_folded')})
    m = m.field('dct:bibliographicCitation', 'string', index='analyzed', analyzer='standard')
    m = m.field('dct:hasPart', 'string', index='analyzed')
    m = m.field('dct:isPartOf', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('dct:issued', 'string', index='analyzed')
    m = m.field('dct:language', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('dct:subject', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('dct:title', 'string', index='analyzed', fields={'folded': dsl.String(analyzer='text_folded')})
    m = m.field('rdau:contentType', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:dissertationOrThesisInformation', 'string', index='analyzed')
    m = m.field('rdau:mediaType', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:modeOfIssuance', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:noteOnResource', 'string', index='not_analyzed')
    m = m.field('rdau:placeOfPublication', dsl.Object().property('@id', 'string', index='not_analyzed'))
    m = m.field('rdau:publicationStatement', 'string', index='analyzed')
    m = m.field('rdfs:isDefinedBy', dsl.Object().property('@id', 'string', index='analyzed', analyzer='extr_id'))
    # Save the mapping in ES
    pprint(m.to_dict(), stream=stream)
    # m.save(esindex, using=escon)


def gendocu(stream, estype='document'):
    """
    Creates the mapping for type document in Elasticsearch
    :param estype: Name of ES type (defaults to 'document')
    """
    m = dsl.Mapping(estype)
    # Set properties
    m.properties.dynamic = 'strict'
    # Adding mapping
    m = gencontext(m)
    m = m.field('@id', 'string', index='not_analyzed')
    m = m.field('@type', 'string', index='no')
    m = m.field('dc:contributor', 'string', index='analyzed', analyzer='autocomplete')
    access = dsl.Object()
    access = access.property('@type', 'string')
    access = access.property('@value', 'date', format='dateOptionalTime')
    m = m.field('dct:issued', access)
    m = m.field('dct:modified', access)
    m = m.field('foaf:primaryTopic', dsl.Object().property('@id', 'string', index='not_analyzed'))
    # Save the mapping in ES
    pprint(m.to_dict(), stream=stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Creates the mapping for Elasticsearch")
    # parser.add_argument('type', metavar='<name>', type=str, help='Name of ES type')
    parser.add_argument('outputfile', metavar='<file>', type=str, help='Output file')
    args = parser.parse_args()

    of = open(args.outputfile, mode='w')
    genbibres(of)
    gendocu(of)
    of.close()