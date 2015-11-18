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
import os
from datetime import datetime
#don't forget to install dependency rdflib-jsonld (serializer plugin for jsonld)


class Rdfxml2Es:

    def __init__(self, file, frame, host, port, esindex, indctrl, bulksize, devmode, filemode, outsubDir):
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
        :param filemode:
        :param outsubDir:
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
        self.filemode = filemode
        self.esdocs = list()
        self.outsubDir = outsubDir
        self.numberOfFilesInSubDir = 300
        self.openedFilesInSubDir = 0
        self.currentSubDir = 1
        self.writtenDocuments = 0
        if self.devmode > 0:
            self.doccounter = 0
        if self.filemode:
            self._openFile()
            #self.of = open('output.json', 'w')
        else:
            try:
                h1 = client.HTTPConnection(self.host, self.port)
                h1.connect()
                h1.close()
                self.of = Elasticsearch([{'host': self.host, 'port': self.port}])
                if  not self.of.indices.exists(self.index) is True:
                    if self.indctrl is not None:
                        self.of.indices.create(index=self.index, body=self.loadjson(self.indctrl))
                    else:
                        self.of.indices.create(index=self.index)
            except Exception as inst:
                exit("Error: " + inst.args[1])

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
        if self.filemode:
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
        if not self.filemode:
            self.bulknum += 1
        self.esdocs.append(self.rdf2es(string, bibo))

        if self.filemode:
            # Output content to file
            #I think we shouldn't serialize the content in memory in the output-file mode

            for outer in self.esdocs:
                for inner in outer:
                    #self.of.write(dumps(inner, separators='\n'))
                    #we need this json dump method because the content is stored in a dictionary structure - as far as I understand it
                    #so we can't just write a string
                    dump(inner, self.of)
                    #dump(bytes(inner,'UTF-8'), self.of)
                    self.writtenDocuments += 1

                    self.of.write('\n')
            #perhaps flush it only in bigger chunks? - later
            #self.of.flush()
            del self.esdocs[:]
            if self.writtenDocuments >= self.bulksize:
                self._closeFile()
                self.writtenDocuments = 0
                self._openFile()

        elif self.bulknum >= self.bulksize:
            # Perform bulk upload
            helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)
            # Reset counter and empty list
            self.bulknum = 0
            del self.esdocs[:]

    def _openFile(self):

        subDir = self.outsubDir + os.sep + self.currentSubDir.__str__()

        if not os.path.isdir(subDir):
            os.mkdir(subDir)
        #every time the script is started, the number of current subdirs is again 1 so we neeed to check
        #hown much files are already stored in the current subdir
        elif self.openedFilesInSubDir >= self.numberOfFilesInSubDir or len([name for name in os.listdir(subDir)]) \
                >= self.numberOfFilesInSubDir:
            self.currentSubDir += 1
            subDir = self.outsubDir + os.sep + self.currentSubDir.__str__()
            if not os.path.isdir(subDir):
                os.mkdir(subDir)
            self.numberOfFilesInSubDir = 0

        outfile = "es." + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + datetime.now().microsecond.__str__() + ".json"

        #using compressed method we are getting difficulties with the gzip interface in combination with the dump method of json module
        #outfile = "es." + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + datetime.now().microsecond.__str__() + ".json.gz"
        absoluteFileName = "".join([subDir,os.sep, outfile])
        self.of = open(absoluteFileName,'w')
        #self.of = gzip.open(absoluteFileName,'wb')

        self.numberOfFilesInSubDir += 1

    def _closeFile(self):
        if not self.of is None:
            #last return necessary for bulk API
            self.of.write("\n")
            self.of.flush()
            name = self.of.name
            self.of.close()
            os.system("gzip " + name)
        self.of = None


class OneLineXML(Rdfxml2Es):

    def parsexml(self):
        with open(self.file) as rdfxml:
            docstart = re.compile('<bibo:Document|<dct:BibliographicResource')
            xmlstart = re.compile('<?xml version')
            pRdfstart = re.compile('.*?(<rdf:RDF.*$)')
            bibo = re.compile('<bibo:Document')
            header = str()
            footer = '</rdf:RDF>'
            for line in rdfxml:
                if self.devmode > 0:
                    self.doccounter += 1
                    if self.doccounter > self.devmode + 2:
                        break
                if docstart.search(line):
                    doc = header + self.stripchars(line) + footer
                    self.bulkupload(doc, bibo.search(doc))
                    continue #make it a little bit faster
                searchedRootTag = pRdfstart.search(line)
                #header is always before document line
                if (searchedRootTag):
                    header += searchedRootTag.group(1)
            # if we are not in the output - file mode upload the bulk to ES
            if not self.filemode and len(self.esdocs) > 0:
                #if we want to write to ES in file-mode we get an error because the client
                #for the helper module then is of file-IO iterator which causes an exception
                #if we want both we have to chnge the current implementation
                helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)
        if self.filemode and not self.of is None:
            #close output file
            self._closeFile()


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
            if not self.filemode and len(self.esdocs) > 0:
                helpers.bulk(client=self.of, actions=self.esdocs, stats_only=True)
        if self.filemode and not self.of is None:
            #close output file
            self._closeFile()





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
    parser.add_argument('--filemode', action='store_true', dest='filemode', help='Do we want to write content in files using the ES _bulk API?. Defaults to False')
    parser.add_argument('--outsubDir', type=str, dest='outsubDir', help='base directory for subdirs where we want to store the Json content in filemode - defaults to /tmp', default='/tmp')
    args = parser.parse_args()
    
    if args.oneline:
        obj = OneLineXML(args.file, args.frame, args.host, args.port, args.index,
                         args.indctrl, args.bulksize, args.devmode, args.filemode, args.outsubDir)
    else:
        obj = MultiLineXML(args.file, args.frame, args.host, args.port, args.index,
                           args.indctrl, args.bulksize, args.devmode, args.filemode, args.outsubDir)
    # If devmode is enabled, count the elapsed time
    if args.devmode > 0:
        from time import time
        start_time = time()
        obj.parsexml()
        print('Elapsed time for', args.devmode, 'elements @', args.bulksize, 'docs per bulk upload:',
              "{0:.2f}".format(round((time() - start_time), 2)), 'seconds')
    else:
        obj.parsexml()