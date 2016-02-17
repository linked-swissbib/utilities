
#from pymongo.connection import Connection
from pymongo import MongoClient
#from bson.binary import Binary



class MongoWrapper():

    def __init__(self):
        #self.connection =  Connection("mongodb://localhost:29017/admin")
        self.client = MongoClient("mongodb://sb-db4.swissbib.unibas.ch:29017/admin")
        #self.client = MongoClient("mongodb://localhost:29017/admin")
        self.solrDB = self.client["solr"]
        self.collection = self.solrDB["queries"]

    def getCollection(self):
        return self.collection


    def closeConnections(self):
        if not self.client is None:
            self.client.close()