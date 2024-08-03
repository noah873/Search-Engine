from urllib.request import urlopen
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup, Comment

from db_connection import connectDatabase
db = connectDatabase()

class Frontier: # this class serves as a queue of urls for the crawler, keeping track of urls to search and urls that have already been visited
    def __init__(self, seedURL):
        self.urls = {seedURL} # to be used as a queue
        self.visitedURLs = set()

    def addURL(self, url): # adds urls to the "bottom" of the queue
        self.urls.add(url)

    def nextURL(self): # pops url from the "top" of the queue, adds it to visitedURLs
        url = self.urls.pop()
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

def target_page(html): # determines if page (URL) contains all 6 classes of Default Header Section Pattern, also checking the Department Name
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
            return True

    return False

def isVisible(text):  # function used by storePage(), returns True if text is visible, otherwise False
    if text.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(text, Comment):
        return False
    return True

def extractText(html): # function used by storePage()
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.findAll(text=True)  # creates array of text
    visibleText = filter(isVisible, text)  # filters text so only visible text remains
    return " ".join(
        text.strip() for text in visibleText)  # removes newline chars with split() and rejoins all visible text

def extractSections(soup, cssClass): # function used by storePage()
    sections = []

    for section in soup.find_all(class_ = cssClass):
        title = section.find('h2').get_text() # Extract title from the <h2> tag
        text = extractText(str(section)) # Extract all text (including title)
        text = text.replace(title, "", 1) # Remove title from text (only 1 replacement max)

        sections.append({
            "title": title,
            "text": text
        })

    return sections

def storePage(url, html): # extracts search areas from webpage and stores it in MongoDB db.pages
    soup = BeautifulSoup(html, 'html.parser')
    blurbs = extractSections(soup, 'blurb') # blurbs are rows in the body (center column)
    accolades = extractSections(soup, 'accolades') # accolades are rows in the sidebar (right column)

    page = {
        "url": url,
        "body": blurbs,
        "sidebar": accolades
    }

    db.pages.insert_one(page) # insert page into MongoDB db.pages
    print(f"Stored Page: '{url}'")
    
def parse(html, url):
    if html is None: # works with the error handling output from retrieveURL (HTTP Error 404, etc.)
        return set() # return an empty set because no urls can be gathered

    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for link in soup.find_all('a', href = True):
        href = link['href']
        absoluteURL = urljoin(url, href)  # Use base url for conversion
        if urlparse(absoluteURL).netloc.endswith('.cpp.edu'): # checks that the url has the domain and TLD of "cpp.edu"
            # removes all characters from the last forward slash to the end of the URL
            # i.e. filters the URLs so that each page is on its "homepage" as many pages share target headers
            parsedURL = urlparse(absoluteURL)
            path = parsedURL.path
            index = path.rfind('/') # index of the last forward slash character
            newPath = path[:index]
            modifiedURL = urlunparse(parsedURL._replace(path = newPath, fragment = ""))

            urls.add(modifiedURL)
    return urls

def crawlerThread(frontier, num_targets):
    targets_found = 0

    while not frontier.done(): # while there are unvisited URLs in the Frontier object
        url = frontier.nextURL()
        html = retrieveURL(url)

        if target_page(html):
            storePage(url, html) # I moved this line down from the pseudocode so only target pages are stored in MongoDB
            targets_found += 1

        if targets_found == num_targets:
            frontier.clear()
        else:
            for url in parse(html, url): # all links on the page are collected, url is inputted as the base url to absolute relative links
                if url not in frontier.visitedURLs:
                    frontier.addURL(url)