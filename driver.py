from pymongo import MongoClient
from crawler import * # Frontier class and crawlerThread() function imported
from text_transformation import transformPages  # Import text transformation function

def connectDatabase(): # to import into other files to access database
    client = MongoClient('mongodb://localhost:27017/')
    db = client['search_engine']
    return db

def main():
    seedURL = "https://www.cpp.edu/cba/international-business-marketing/index.shtml"
    frontier = Frontier(seedURL) # Frontier class acts like a queue, initialized with just the seed url
    num_targets = 10 # crawler will run until it has found and stored the information of this many target pages

    crawlerThread(frontier, num_targets) # crawls webpages from seed URL and saves areas of search of target pages in MongoDB db.pages

    transformPages() # performs text transformation on db.pages

if __name__ == "__main__":
    main()