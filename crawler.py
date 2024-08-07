from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from db_connection import connectDatabase
db = connectDatabase()

class Frontier: # this class serves as a queue of urls for the crawler, keeping track of urls to search and urls that have already been visited
    def __init__(self, seedURL):
        self.urls = [seedURL] # to be used as a queue
        self.visitedURLs = set()

    def addURL(self, url): # adds urls to the "bottom" of the queue
        self.urls.append(url)

    def nextURL(self): # pops url from the "top" of the queue, adds it to visitedURLs
        url = self.urls.pop(0)
        self.visitedURLs.add(url)
        return url

    def done(self): # returns True if all urls in queue have been searched, otherwise False
        return len(self.urls) == 0

    def clear(self):
        self.urls.clear()
        self.visitedURLs.clear()

def retrieveURL(url):
    try:
        response = urlopen(url)
        html = response.read()
        return html
    except Exception as e:
        print(f"Error Retrieving URL: '{url}', {e}")
    return None

def target_page(url, html): # determines if page (URL) contains all 6 classes of Default Header Section Pattern, also checking the Department Name
    if html is None: # works with the error handling output from retrieveURL (HTTP Error 404, etc.)
        return False

    soup = BeautifulSoup(html, 'html.parser')
    classNames = ['fac-info', 'title-dept', 'emailicon', 'phoneicon', 'locationicon', 'hoursicon']
    for className in classNames:
        if not soup.find(class_ = className):
            return False

    departmentVariations = [
        "International Business Marketing",
        "International Business & Marketing",
        "International Business and Marketing",
        "IBM"
    ]

    for departmentName in departmentVariations:
        if departmentName in soup.find('span', class_ = 'title-dept').get_text():
            db.crawled_pages.update_one({"url": url}, {"$set": {"isTarget": True}})
            print(f"Found Target Page: '{url}'")

            return True

    return False
    
def parse(html, url):
    if html is None: # works with the error handling output from retrieveURL (HTTP Error 404, etc.)
        return [] # return an empty array because no urls can be gathered

    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for link in soup.find_all('a', href = True):
        href = link['href']
        absoluteURL = urljoin(url, href)  # Use base url for conversion
        if absoluteURL not in urls:
            urls.append(absoluteURL)

    return urls

def storePage(url, html):
    page = {
        "url": url,
        "html": html,
        "isTarget": False
    }
    try:
        db.crawled_pages.insert_one(page)  # insert page into MongoDB db.pages
        print(f"Stored Page: '{url}'")
    except Exception as e:
        print(f"Error Storing Page: '{url}', {e}")

def crawlerThread(frontier, num_targets):
    targets_found = 0

    while not frontier.done(): # while there are unvisited URLs in the Frontier object
        url = frontier.nextURL()
        html = retrieveURL(url)

        storePage(url, html)
        if target_page(url, html): # marks page document as target
            targets_found += 1

        if targets_found == num_targets:
            frontier.clear()
        else:
            for url in parse(html, url): # all links on the page are collected, url is inputted as the base url to absolute relative links
                if url not in frontier.visitedURLs:
                    frontier.addURL(url)
