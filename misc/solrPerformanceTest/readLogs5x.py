# -*- coding: utf-8 -*-
import sys
#import pymongo.connection
#from pymongo.connection import Connection
#from bson.binary import Binary

from MongoWrapper import MongoWrapper



__author__ = 'swissbib'


import re

class ParseLogLine():
    def __init__(self,shortquery,longquery):
        self.numberLinesWritten = 0
        self.qLine = re.compile("params={(.*?)}")
        self.qLineSolr5 = re.compile("params={(.*?)} hits")
        self.qOnly = re.compile("&q=(.*?)&")
        self.qOnlyList = []
        #self.shortqueryFile = open(shortquery,"a")
        #self.longqeryFile = open(longquery,"a")

        self.numberHits = re.compile("hits=(\d+)")

        # QTime=1
        self.qTime = re.compile("QTime=(\d+)")

        #self.host = "mongodb://admin:ayKejO3k@sb-db5.swissbib.unibas.ch:29017/admin"

        self.mongoWrapper = MongoWrapper()


        self.jMeterQueries = ["%2Bthe+%2Bart+%2Bof+%2Bcomputer+%2Bprogramming",
                              "q=Faust","event=newSearcher",
                              "start=0&q=%2Bsublocal_B1:[*+TO+*]%0a%0a%2B(%0asubtop_swd:[*+TO+*]++OR+%0asubpers_swd",
                              "Basler+Zeitschrift+für+Geschichte+und+Altertumskunde",
                              "start=0&q=%2Bsublocal_BY:[*+TO+*]%0a%0a%2B(%0asubtop_idsbb",
                              "start=0&q=%2B(%0asubtop_rero:[*+TO+*]++OR+%0asubpers_rero:[*+TO+*]",
                              "start=0&q=%2Bsublocal_BP",
                              "start=0&q=%2Bsublocal_BU",
                              "start=0&q=%2Bsublocal_BW",
                              "start=0&q=%2Bsublocal_G1",
                              "start=0&q=%2Bsublocal_G3",
                              "start=0&q=%2Bsublocal_G5",
                              "start=0&q=%2Bsublocal_G7",
                              "start=0&q=%2Bsublocal_G9",
                              "start=0&q=%2Bsublocal_GC",
                              "start=0&q=%2Bsublocal_GF",
                              "file=schema.xml&contentType=text/xml",
                              "file=admin-extra",
                              "file=solrconfig.xml",
                              "command=details",
                              "numTerms=0&show=index",
                              #"wt=json",
                              "q=title_long:The+art+of+computer+programming&rows=2",
                              "touchpoint/perma.do"]
        self.relevantQueries = ["facet=true"]


    def __del__(self):
        #sys.stdout.write("\n".join(self.qOnlyList))
        #self.shortqueryFile.write("\n".join(self.qOnlyList))
        #self.shortqueryFile.close()
        #self.longqeryFile.close()
        if not self.mongoWrapper is None:
            self.mongoWrapper.closeConnections()



    def evaluate(self,line):
        #qValue = self.qLine.search(line)
        qValue = self.qLineSolr5.search(line)
        wanted = False
        if qValue:
            query = qValue.group(1)
            for item in self.jMeterQueries:
                if query.find(item) != -1:
                    return
            for item in self.relevantQueries:
                
                if query.find(item) != -1:
                    wanted = True



            if wanted:
                q1 = query.replace("&wt=javabin","&wt=json")
                q2 = q1.replace("&version=2","")

                nHits = self.numberHits.search(line)
                qT = self.qTime.search(line)
                if nHits and qT:
                    hits = (int)(nHits.group(1))
                    time = (int)(qT.group(1))
                    if hits > 1:

                        self.numberLinesWritten += 1
                        newrecord = {
                         "query":q2,
                         "time":(int)(time),
                         "hits":(int)(hits)
                        }

                        try:

                            self.mongoWrapper.getCollection().insert(newrecord)
                        except Exception as pythonBaseException:

                            print pythonBaseException


    def getNumberOfWrittenQueries(self):
        return self.numberLinesWritten




if __name__ == '__main__':

    import os
    from argparse import ArgumentParser





    oParser = ArgumentParser()
    oParser.add_argument("-d", "--dir", dest="directory")
    oParser.add_argument("-l", "--longqueryFile", dest="wholequeryFile", default="./longquery.txt")
    oParser.add_argument("-s", "--shortqueryFile", dest="queryFile", default="./shortquery.txt")



    args = oParser.parse_args()


    tDir = args.directory

    longqueryFile= args.wholequeryFile
    shortqueryFile = args.queryFile

    numberOfLines = 0
    os.chdir(tDir)
    for fname in os.listdir(tDir):
        sys.stdout.write("".join(["\n\n","-----",fname,"-----","\n"]))
        iF =  open (fname,"r")
        pLog = ParseLogLine(shortqueryFile,longqueryFile)
        for line in iF:
            pLog.evaluate(line)

        numberOfLines += pLog.getNumberOfWrittenQueries()

    sys.stdout.write("".join(["\n\n","-----","number of queries: ",str(numberOfLines),"-----","\n"]))


