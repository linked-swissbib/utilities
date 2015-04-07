# -*- coding: utf-8 -*-

__author__ = 'swissbib'

import re
from argparse import ArgumentParser

#inputFile = "data/job1r109A090.format.xml"
#outputFile = 'data/correctMarcXML.xml'

#simple script to insert an additional type attribute. Background:
#because Metafacture requires a type attribute in the record element -which isn't provided by CBS so far - we need to insert this attribute in the records exported by swissbib



oParser = ArgumentParser()
oParser.add_argument("-i", "--inFile", dest="inputFile",default=None)
oParser.add_argument("-o", "--outFile", dest="outputFile", default=None)




args = oParser.parse_args()
iF = args.inputFile
oF = args.outputFile



fileCorrectMarcXML = open (oF,"w")

collectionPattern = re.compile('<collection>',re.UNICODE | re.DOTALL | re.IGNORECASE)


for line in open(iF,"r"):
    if line.find('<collection>') != -1:

        #fileCorrectMarcXML.write('<collection xmlns="http://www.loc.gov/MARC21/slim" ')
        newLine = re.sub(pattern= '<collection>', repl= '<collection xmlns="http://www.loc.gov/MARC21/slim" >',string=line, flags= re.UNICODE | re.DOTALL | re.IGNORECASE)
        fileCorrectMarcXML.write(newLine)

    elif line.find('<record>') != -1:
        newLine = re.sub(pattern= '<record>', repl= '<record type="Bibliographic">', string=line, flags= re.UNICODE | re.DOTALL | re.IGNORECASE)
        fileCorrectMarcXML.write(newLine)
    else:
        fileCorrectMarcXML.write(line)

fileCorrectMarcXML.close()