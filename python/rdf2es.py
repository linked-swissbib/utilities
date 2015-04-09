#!/usr/bin/python3

# The Script is an adaptation of the one discussed on http://journal.code4lib.org/articles/7949

import json
import subprocess
import argparse
import elasticsearch
import re
import pprint
from pyld import jsonld
from http import client
import sys


class Rdf2JsonLD:

    def __init__(self, ifile, frame, rdfformat, docs, mapping):
        self.ifile = ifile
        self.frame = frame
        self.format = rdfformat
        self.docs = docs
        self.map = mapping
        self.nquads = str()
        self.offsets = list()
        self.newdoc = list()

    def parserdf(self):
        print("Parsing RDF file")
        self.nquads = subprocess.check_output(['rapper', '-i', self.format, '-o', 'nquads', self.ifile],
                                              universal_newlines=True)

    def sequencerdf(self):
        print("Sequencing RDF file")
        # Search for subjects in nquad triples
        pattern = re.compile('^(<.*?>)', re.MULTILINE)
        subjects = pattern.findall(self.nquads)
        # Identify row numbers of new subjects
        i = 1
        self.newdoc = [0]
        for subj in subjects[0:len(subjects)-2]:
            if subj != subjects[i]:
                self.newdoc.append(i)
            i += 1
        # Get offsets of linebreaks. First token of new line begins at index offset + 1,
        # last token is at index <next offset>
        self.offsets = [-1]
        self.offsets.extend([m.start() for m in re.finditer('\n', self.nquads)])
        self.offsets.append(len(self.nquads)-1)
        # newdoc serves as an index to offsets list: newdoc[0] signifies offset=0,
        # newdoc[len(offsets)-1] means very last token of nquads.
        self.newdoc.append(len(self.offsets) - 1)
        self.newdoc.sort()

    def output(self, doc):
        pass

    def rdf2jsonld(self):
        # Extract tokens from offset + 1 to <n-th offset after> (n = args.docs)
        i = 0
        while i < len(self.newdoc) - 1:
            if i + self.docs >= len(self.newdoc) - 1:
                j = len(self.newdoc) - 1
            else:
                j = i + self.docs
            # Serializing RDF into JSON-LD by method from_rdf results in the so called
            # expanded document form, i.e. a format that doesn't contain any namespaces
            print("Serializing RDF file to JSON-LD")
            expand = jsonld.from_rdf(self.nquads[self.offsets[self.newdoc[i]] + 1:self.offsets[self.newdoc[j]]])
            i = j
            # The compacted JSON-LD document form offers the possibility to include a context
            # (i.e. namespaces) and thus reduces redundancy
            print("Converting to compacted document form")
            compacted = jsonld.compact(expand, json.load(open(self.frame, 'r')))
            print("Indexing documents")
            for graph in compacted["@graph"]:
                graph["@context"] = compacted["@context"]
                self.output(graph)


class JsonLD2ES(Rdf2JsonLD):

    def __init__(self, ifile, frame, esindex, estype, rdfformat, docs, mapping, host, port):
        Rdf2JsonLD.__init__(self, ifile, frame, rdfformat, docs, mapping)
        self.index = esindex
        self.type = estype
        try:
            self.of = elasticsearch.Elasticsearch([{'host': host, 'port': port}])
            h1 = client.HTTPConnection(host, port)
            h1.connect()
            h1.close()
        except Exception as inst:
            sys.exit("Error:" + inst.args[1])

    def output(self, doc):
        self.of.index(index=self.index, doc_type=self.type, body=doc)


class JsonLD2File(Rdf2JsonLD):

    def __init__(self, ifile, frame, rdfformat, docs, mapping, ofile):
        Rdf2JsonLD.__init__(self, ifile, frame, rdfformat, docs, mapping)
        try:
            self.of = open(ofile, mode='x')
        except Exception as inst:
            sys.exit("Error:" + inst.args[1])

    def output(self, doc):
        pprint.pprint(doc, stream=self.of)

    def __del__(self):
        self.of.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Indexing RDF file in Elasticsearch")
    parser.add_argument('ifile', metavar='<filename>', type=str, help='Path to ')
    parser.add_argument('frame', metavar='<filename>', type=str, help='Path to JSON-LD frame file')
    parser.add_argument('--host', metavar='<ip>', type=str, default='localhost', help='Ip of search engine host')
    parser.add_argument('--port', metavar='<port>', type=int, default=9200, help='Port number of search engine')
    parser.add_argument('--index', metavar='<str>', dest='index', type=str, default='triples',
                        help='Name of Elasticsearch index. Defaults to \'triples\'')
    parser.add_argument('--type', metavar='<str>', dest='type', type=str, default='rdf',
                        help='Name of Elasticsearch type. Defaults to \'rdf\'')
    parser.add_argument('--format', metavar='<format>', dest='format', type=str,
                        choices=['rdfxml', 'ntriples', 'turtle', 'trig', 'rss-tag-soup', 'grddl', 'guess',
                                 'rdfa', 'json', 'nquads'], default='turtle',
                        help='''Format of RDF file. Possible values are: rdfxml', 'ntriples', 'turtle', 'trig',
                    'rss-tag-soup', 'grddl', 'rdfa', 'json', 'nquads' and 'guess'. Defaults to 'turtle'.''')
    parser.add_argument('--docs', metavar='<int>', dest='docs', type=int, default=50,
                        help='Maximum number of documents to be processed at the same time. Defaults to 20.')
    parser.add_argument('--output', metavar='<filename>', dest='output', type=str,
                        help='Outputs JSON-LD documents to file instead of indexing in Elasticsearch.')
    parser.add_argument('--map', metavar='<filename>', dest='map', type=str,
                        help='File containing a special mapping for Elasticsearch indexing. ')
    args = parser.parse_args()

    if args.output is None:
        obj = JsonLD2ES(ifile=args.ifile,
                        frame=args.frame,
                        esindex=args.index,
                        estype=args.type,
                        rdfformat=args.format,
                        docs=args.docs,
                        mapping=args.map,
                        host=args.host,
                        port=args.port)
    else:
        obj = JsonLD2File(ifile=args.ifile,
                          frame=args.frame,
                          rdfformat=args.format,
                          docs=args.docs,
                          mapping=args.map,
                          ofile=args.output)
    obj.parserdf()
    obj.sequencerdf()
    obj.rdf2jsonld()