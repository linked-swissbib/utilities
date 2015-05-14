__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.2'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

import re
from rdflib import Graph
from pyld import jsonld
from jsmin import jsmin
from json import loads, dump
from elasticsearch import Elasticsearch, helpers
from http import client
import argparse


class Rdfxml2Es:

    def __init__(self, file, frame, host, port, esindex, indctrl, bulksize, devmode, outfile):
        """
        1) Initializes some attributes
        2) Checks if connection to ES node can be established
        3) Checks if ES index does not already exist
        4) If 2) und 3) are true, then create index and type mappings

        :param file: The RDF-XML file
        :param frame: File containing the JSON-LD framing
        :param host: Host of ES node
        :param port: Port of ES node
        :param esindex: Name of ES index
        :param indctrl: Settings and mapping for ES
        :param bulksize: Size of bulk uploads
        :param devmode: Number of samples for performing performance
        :param outfile: File output instead of indexing
        test on different bulk upload sizes
        :return: None
        """
        self.file = file
        self.frame = frame
        self.host = host
        self.port = port
        self.index = esindex
        self.indctrl = indctrl
        self.bulksize = bulksize
        self.bulknum = 0
        self.devmode = devmode
        self.outfile = outfile
        self.esdocs = list()
        if self.devmode > 0:
            self.doccounter = 0
        if self.outfile:
            self.of = open('output.json', 'w')
        else:
            try:
                h1 = client.HTTPConnection(self.host, self.port)
                h1.connect()
                h1.close()
                self.of = Elasticsearch([{'host': self.host, 'port': self.port}])
                if self.of.indices.exists(self.index):
                    raise Exception('Error', 'Elasticsearch index already exists.')
            except Exception as inst:
                exit("Error: " + inst.args[1])
            else:
                if self.indctrl is not None:
                    self.of.indices.create(index=self.index, body=self.loadjson(self.indctrl))
                else:
                    self.of.indices.create(index=self.index)

    @staticmethod
    def loadjson(ifile):
        """
        Loads a file containing valid JSON-LD objects and removes comments
        :param ifile:
        :return: Object of type Dictionary
        """
        with open(ifile, 'r') as f:
            raw = f.read()
        jsonstr = jsmin(raw)
        return loads(jsonstr)

    @staticmethod
    def stripchars(string):
        """
        Removes tabs and newlines from string.
        :param string:
        :return: Cleaned string
        """
        return ''.join(re.split('\t+|\n+', string))

    def parsexml(self):
        """
        Parses XML and kicks off the transformation and indexing of the individual documents.
        Must be implemented in child classes
        :return: None
        """
        raise NotImplementedError

    def rdf2es(self, string, bibo):
        """
        Does the really interesting stuff: Transformation of the
        triples by subject and indexing in ES
        :param string: The RDF triples as a concatenated string.
        :param bibo: Is subject a bibo:Document?
        :return: Body for ES indexing
        """
        g = Graph().parse(data=string)
        jldstr = g.serialize(format='json-ld',
                             indent=4)
        if bibo:
            esdoc = jsonld.compact(loads(jldstr.decode('utf-8')), self.loadjson(self.frame))
            doctype = 'document'
        else:
            esdoc = loads(jldstr.decode('utf-8'))
            esdoc = jsonld.frame(esdoc, self.loadjson(self.frame))['@graph'][0]
            esdoc['@context'] = self.loadjson(self.frame)['@context']
            doctype = 'bibliographicResource'
        docid = re.findall('\w{9}', esdoc['@id'])[0]
        if self.outfile:
            bulkfile = [{'index': {'_index': self.index, '_type': doctype, '_id': docid}}, esdoc]
            return bulkfile
        else:
            esdoc.update({'_index': self.index, '_type': doctype, '_id': docid})
            return esdoc

    def bulkupload(self, string, bibo):
        """
        Creates a list of single JSON-LD documents and indexes them as bulk upload
        :param string: The RDF triples as a concatenated string.
        :param bibo: Is subject a bibo:Document?
        :return:
        """
        self.bulknum += 1
        self.esdocs.append(self.rdf2es(string, bibo))
        if self.bulknum >= self.bulksize:
            if self.outfile:
                # Output content to file
                for outer in self.esdocs:
                    for inner in outer:
                        # pp = PrettyPrinter(indent=0, width=100000, stream=self.of, compact=True)
                        # pp.pprint(inner)
                        #self.of.write(dumps(inner, separators='\n'))
                        dump(inner, self.of)
                        self.of.write('\n')
            else:
                # Perform bulk upload
                helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)
            # Reset counter and list
            self.bulknum = 0
            del self.esdocs[:]


class OneLineXML(Rdfxml2Es):

    def parsexml(self):
        with open(self.file) as rdfxml:
            docstart = re.compile('<bibo:Document|<dct:BibliographicResource')
            xmlstart = re.compile('<?xml version')
            rdfstart = re.compile('<rdf:RDF')
            bibo = re.compile('<bibo:Document')
            header = str()
            footer = '</rdf:RDF>'
            for line in rdfxml:
                if self.devmode > 0:
                    self.doccounter += 1
                    if self.doccounter > self.devmode + 2:
                        break
                if xmlstart.search(line):
                    header = self.stripchars(line)
                elif rdfstart.search(line):
                    header += self.stripchars(line)
                elif docstart.search(line):
                    doc = header + self.stripchars(line) + footer
                    self.bulkupload(doc, bibo.search(doc))
                else:
                    continue
            # Upload last bulk
            if len(self.esdocs) > 0:
                helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)


class MultiLineXML(Rdfxml2Es):

    def parsexml(self):
        with open(self.file) as rdfxml:
            docstart = re.compile('<bibo:Document|<dct:BibliographicResource')
            xmlstart = re.compile('<?xml version')
            rdfstart = re.compile('<rdf:RDF')
            docend = re.compile('</bibo:Document|</dct:BibliographicResource')
            bibo = re.compile('<bibo:Document')
            reclines = False
            doc = str()
            header = str()
            footer = '</rdf:RDF>'
            for line in rdfxml:
                if self.devmode > 0:
                    self.doccounter += 1
                    if self.doccounter > self.devmode + 2:
                        break
                if xmlstart.search(line):
                    header = self.stripchars(line)
                elif rdfstart.search(line):
                    header += self.stripchars(line)
                elif docstart.search(line):
                    reclines = True
                    doc = header + self.stripchars(line)
                elif docend.search(line):
                    doc += self.stripchars(line) + footer
                    self.bulkupload(doc, bibo.search(doc))
                    reclines = False
                elif reclines:
                    doc += self.stripchars(line)
                else:
                    continue
            # Upload last bulk
            if len(self.esdocs) > 0:
                helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Indexing RDF/XML triples in Elasticsearch")
    parser.add_argument('file', metavar='<filename>', type=str, help='Path to RDF/XML file')
    parser.add_argument('frame', metavar='<filename>', type=str, help='Path to JSON-LD frame file')
    parser.add_argument('--host', metavar='<ip>', type=str, default='localhost', help='Ip of search engine host')
    parser.add_argument('--port', metavar='<port>', type=int, default=9200, help='Port number of search engine')
    parser.add_argument('--index', metavar='<str>', dest='index', type=str, default='testsb',
                        help='Name of Elasticsearch index. Defaults to \'testsb\'')
    parser.add_argument('--indctrl', metavar='<filename>', dest='indctrl', type=str,
                        help='File containing settings and mappings for Elasticsearch indexing.')
    parser.add_argument('--bulksize', metavar='<int>', dest='bulksize', type=int, default=1000,
                        help='Size of bulk uploads.')
    parser.add_argument('--oneline',  action='store_true',  dest='oneline',
                        help='Are RDF/XML-documents in input file on one or multiple lines? Defaults to False')
    parser.add_argument('--devmode', metavar='<int>', dest='devmode', type=int, default=0,
                        help='Count the time for a specified amount of samples. Defaults to 0')
    parser.add_argument('--outfile', metavar='<boolean>', dest='outfile', type=bool, choices=[True, False],
                        default=False, help='File output. Defaults to False')
    args = parser.parse_args()
    
    if args.oneline:
        obj = OneLineXML(args.file, args.frame, args.host, args.port, args.index,
                         args.indctrl, args.bulksize, args.devmode, args.outfile)
    else:
        obj = MultiLineXML(args.file, args.frame, args.host, args.port, args.index,
                           args.indctrl, args.bulksize, args.devmode, args.outfile)
    # If devmode is enabled, count the elapsed time
    if args.devmode > 0:
        from time import time
        start_time = time()
        obj.parsexml()
        print('Elapsed time for', args.devmode, 'elements @', args.bulksize, 'docs per bulk upload:',
              "{0:.2f}".format(round((time() - start_time), 2)), 'seconds')
    else:
        obj.parsexml()