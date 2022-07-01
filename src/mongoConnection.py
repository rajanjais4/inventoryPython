import constants
import pymongo
import sys
sys.path.insert(0, '../..')


##################### Mongo Connection ##############################
class MongoConnection:
    mongoClient = ""

    @classmethod
    def mongoConnect(cls):
        try:
            mongoUri = constants.mongoUri
            print("start connection")
            mongo = pymongo.MongoClient(mongoUri,
                                        serverSelectionTimeoutMs=1000)
            print("mongo connection successfully")
            cls.mongoClient = mongo
            return mongo
        except:
            print("Couldn't connect to Mongo'")
