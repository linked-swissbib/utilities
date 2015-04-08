# -*- coding: utf-8 -*-


__author__ = "Günter Hipler"
__copyright__ = "Copyright 2015, swissbib project, UB Basel"
__license__ = "http://opensource.org/licenses/gpl-2.0.php"
__version__ = "2.0"
__maintainer__ = "Günter Hipler"
__email__ = "guenter.hipler@unibas.ch"
__status__ = "development"

"""
simple and quick script to collect a defined number of records from any repository part of swissbib.
purpose: this enables e.g. a better (more representative) analysis of swissbib records

"""
import re
import os
import gzip


#simple script to


networksLookFor = {
            "RERO",
            "NEBIS",
            "SNL",
            "IDSBB",
            "SGBN" ,
            "IDSLU",
            "ALEX" ,
            "SBT" ,
            "ABN" ,
            "IDSSG" ,
            "BGR" ,
            "RETROS" ,
            "LIBIB",
            "IDSSG2",
            "CCSA" ,
            "ZORA" ,
            "SERVAL",
            "ECOD"
            }



maxNumber = 10000
networks = {"RERO"  : 0,
            "NEBIS" :0,
            "SNL" : 0,
            "IDSBB" :0,
            "SGBN" : 0,
            "IDSLU" :0,
            "ALEX" : 0, #Alexandria
            "SBT" : 0, #Tessin
            "ABN" : 0, #Aargau
            "IDSSG" : 0, #St. Gallen Uni
            "BGR" :0, #Kantonsbibliothek Graubuenden
            "RETROS" : 0,  #retroseals
            "LIBIB" : 0, #Lichtenstein
            "IDSSG2" : 0, #St. Gallen PH / FH
            "CCSA" : 0, #Plakatsammlung - Achtung: diese nicht verteilen!
            "ZORA" : 0,
            "SERVAL": 0, #Lausanne repository
            "ECOD" : 0 # nur 1000 e-codices
            }


networksMaxNumber = {
            "RERO"  : maxNumber,
            "NEBIS" :maxNumber,
            "SNL" : maxNumber,
            "IDSBB" :maxNumber,
            "SGBN" : maxNumber,
            "IDSLU" :maxNumber,
            "ALEX" : maxNumber,
            "SBT" : maxNumber,
            "ABN" : maxNumber,
            "IDSSG" : maxNumber,
            "BGR" : maxNumber,
            "RETROS" : maxNumber,
            "LIBIB" : maxNumber,
            "IDSSG2" : maxNumber,
            "CCSA" : maxNumber,
            "ZORA" : maxNumber,
            "SERVAL": maxNumber,
            "ECOD" : 1000
            }


inDir = "/swissbib_index/solrDocumentProcessing/FrequentInitialPreProcessing/data/format_2"

openFile = open("./representativeData.xml",'w')
openFile.write('<?xml version="1.0" encoding="utf-8" ?>' + os.linesep)
openFile.writelines('<collection xmlns="http://www.loc.gov/MARC21/slim">' + os.linesep)


def writeRecord (line):
    openFile.write(line)
    openFile.flush()


def isDictionaryComplete():

    return len(networksLookFor) == 0





stopJob = False
pLocalIdentifier  = re.compile('tag="035".*?><subfield code="a">(\((.*?)\).*?)</subfield>',re.UNICODE | re.DOTALL | re.IGNORECASE)
for fname in sorted(os.listdir(inDir)):

    with gzip.open(inDir + os.sep + fname, "r") as iterator:

        for line in iterator:
            searchedToken = pLocalIdentifier.search(line)
            if searchedToken:
                localID = searchedToken.group(2)
                if localID in networks and networks[localID] <= networksMaxNumber[localID]:
                    newLine = re.sub(pattern= '<record>', repl= '<record type="Bibliographic">', string=line, flags= re.UNICODE | re.DOTALL | re.IGNORECASE)
                    writeRecord(newLine)
                    networks[localID] +=  1
                    if networks[localID] > networksMaxNumber[localID]:
                        networksLookFor.remove(localID)


                    if isDictionaryComplete():
                        stopJob = True
                        break
    if stopJob:
        break


if openFile is not None:
    openFile.writelines('</collection>' + os.linesep)
    openFile.close()



