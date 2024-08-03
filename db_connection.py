from pymongo import MongoClient

def connectDatabase(): # to import into other files to access database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['search_engine']
    return db