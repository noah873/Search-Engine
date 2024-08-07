from crawler import Frontier, crawlerThread
from parse_target_pages import parseTargetPages
from text_transformation import transformPages  # Import text transformation function
from index_creation import create_index  # Import the create_index function

def main():
    seedURL = "https://www.cpp.edu/cba/international-business-marketing/index.shtml"
    frontier = Frontier(seedURL) # Frontier class acts like a queue, initialized with just the seed url
    num_targets = 22 # crawler will run until it has found this many target pages

    crawlerThread(frontier, num_targets) # crawls webpages from seed URL and saves all pages in db.crawled_pages until num_targets of target pages are found

    parseTargetPages() # extracts areas of search from target pages and saves to db.target_pages

    transformPages() # performs text transformation on db.pages saving output in db.transformed_pages

    create_index() # create the index after transformation

if __name__ == "__main__":
    main()
