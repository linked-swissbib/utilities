#!/usr/bin/python3

# The Script is an adaptation of the one discussed on http://journal.code4lib.org/articles/7949

import json
import subprocess
import argparse
import elasticsearch
import re
from pyld import jsonld
from sys import exit


parser = argparse.ArgumentParser(description="Indexing RDF file in Elasticsearch")
parser.add_argument('ifile', metavar='<RDF file>', type=str, help='Path to inputfile')
parser.add_argument('frame', metavar='<frame file>', type=str, help='Path to JSON-LD frame file')
parser.add_argument('--host', metavar='<ip>', type=str, default='localhost', help='Ip of search engine host')
parser.add_argument('--port', metavar='<port>', type=int, default=9200, help='Port number of search engine')
parser.add_argument('--index', metavar='<string>', dest='index', type=str, default='triples',
                    help='Name of Elasticsearch index. Defaults to \'triples\'')
parser.add_argument('--type', metavar='<string>', dest='type', type=str, default='rdf',
                    help='Name of Elasticsearch type. Defaults to \'rdf\'')
parser.add_argument('--format', metavar='<format>', dest='format', type=str,
                    choices=['rdfxml', 'ntriples', 'turtle', 'trig', 'rss-tag-soup', 'grddl', 'guess',
                             'rdfa', 'json', 'nquads'], default='turtle',
                    help='''Format of RDF file. Possible values are: rdfxml', 'ntriples', 'turtle', 'trig',
                    'rss-tag-soup', 'grddl', 'rdfa', 'json', 'nquads' and 'guess'. Defaults to 'turtle'.''')
parser.add_argument('--docs', metavar='<number>', dest='docs', type=int, default=50,
                    help='Maximum number of documents to be processed at the same time. Defaults to 20.')
args = parser.parse_args()

print("Parsing RDF file")
nquads = subprocess.check_output(['rapper', '-i', args.format, '-o', 'nquads', args.ifile],
                                 universal_newlines=True)

print("Sequencing RDF file")
# Search for subjects in nquad triples
pattern = re.compile('^(<.*?>)', re.MULTILINE)
subjects = pattern.findall(nquads)
# Identify row numbers of new subjects
newdoc = {0}
i = 1
for subj in subjects[0:len(subjects)-2]:
    if subj != subjects[i]:
        newdoc.add(i)
    i += 1
# Get offsets of linebreaks. First token of new line begins at index offset + 1, last token is at index <next offset>
offsets = [-1]
offsets.extend([m.start() for m in re.finditer('\n', nquads)])
offsets.append(len(nquads)-1)
# newdoc serves as an index to offsets list: newdoc[0] signifies offset=0, newdoc[len(offsets)-1] means very last token
# of nquads.
newdoc.add(len(offsets) - 1)
newdoc = sorted(list(newdoc))
# Connect to Elasticsearch
try:
    es = elasticsearch.Elasticsearch([{'host': args.host, 'port': args.port}])
except elasticsearch.ConnectionError:
    exit("Error: Could not connect to search server.")
else:
    # Extract tokens from offset + 1 to <n-th offset after> (n = args.docs)
    i = 0

    while i < len(newdoc) - 1:
        if i + args.docs >= len(newdoc) - 1:
            j = len(newdoc) - 1
        else:
            j = i + args.docs
        # Serializing RDF into JSON-LD by method from_rdf results in the so called
        # expanded document form, i.e. a format that doesn't contain any namespaces
        print("Serializing RDF file to JSON-LD")
        expand = jsonld.from_rdf(nquads[offsets[newdoc[i]] + 1:offsets[newdoc[j]]])
        i = j
        # The compacted JSON-LD document form offers the possibility to include a context
        # (i.e. namespaces) and thus reduces redundancy
        print("Converting to compacted document form")
        compacted = jsonld.compact(expand, json.load(open(args.frame, 'r')))
        print("Indexing documents")
        total = len(compacted["@graph"])
        for graph in compacted["@graph"]:
            graph["@context"] = compacted["@context"]
            res = es.index(index=args.index, doc_type=args.type, body=graph)