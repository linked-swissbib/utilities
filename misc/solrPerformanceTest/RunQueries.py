
from MongoWrapper import MongoWrapper
import requests
import json
from StringIO import StringIO
import time
from datetime import datetime, timedelta


class RunQueries():
    def __init__(self):


        cTimeUTC =  datetime.utcnow()
        nTList = [str(cTimeUTC.date()),"T",str(cTimeUTC.hour),str(cTimeUTC.minute),str(cTimeUTC.second),"Z"]
        self.currentTime = "".join(nTList)


        self.mongoWrapper = MongoWrapper()



    def startRunning(self):
        for doc in self.mongoWrapper.getCollection().find({}):
            try:
                #print query
                query = doc["query"]
                #time = doc["time"]
                #hits = doc["hits"]
                #id = doc["_id"]

                #result = requests.get("http://sb-s1.swissbib.unibas.ch:8080/solr/sb-biblio/select",params=query.encode("utf-8"))
                result = requests.get("http://sb-s20.swissbib.unibas.ch:8080/solr/sb-biblio/select",params=query.encode("utf-8"))
                #result = requests.get("http://search.swissbib.ch/solr/sb-biblio/select",params=query.encode("utf-8"))
                text = result.content
                io = StringIO(text)
                myJson = json.load(io)
                queryTime = myJson["responseHeader"]["QTime"]
                numberHits = myJson["response"]["numFound"]

                doc["solr5QTime" + self.currentTime] = (int)(queryTime)
                doc["solr5hits" + self.currentTime] = (int)(numberHits)

                self.mongoWrapper.getCollection().save(doc)
                #self.mongoWrapper.getCollection().safe(doc,safe=True)


            except Exception,ex:
                print ex




if __name__ == '__main__':


    runner = RunQueries()
    runner.startRunning()




