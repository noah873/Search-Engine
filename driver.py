from pymongo import MongoClient
from crawler import * # Frontier class and crawlerThread() function imported

def connectDatabase(): # to import into other files to access database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['search_engine']
    return db

def main():
    seedURL = "https://www.cpp.edu/cba/international-business-marketing/index.shtml"
    frontier = Frontier(seedURL)
    num_targets = 10

    crawlerThread(frontier, num_targets) # crawls webpages from seed URL and saves areas of search of target pages in MongoDB db.pages

if __name__ == "__main__":
    main()
