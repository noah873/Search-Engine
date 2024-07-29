from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse

from driver import connectDatabase # enables connection to the shared MongoDB database
db = connectDatabase()

class Frontier:
    def __init__(self, seedURL):
        self.urls = {seedURL}
        self.visitedURLs = set()

    def addURL(self, url):
        if url not in self.visitedURLs:
            self.urls.add(url)

    def nextURL(self):
        url = self.urls.pop()
        self.visitedURLs.add(url)
        return url

    def done(self):
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

def store_page(url, html):
    html = BeautifulSoup(html, 'html.parser').prettify()  # temporary
    db.pages.insert_one({'url': url, 'html': html})
    
def parse(html, base_url):
    if html is None: # works with the error handling output from retrieveURL (HTTP Error 404, etc.)
        return set() # return an empty set because no links can be gathered

    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)  # Use base_url for conversion
        if urlparse(absolute_url).netloc.endswith('.cpp.edu'):
            absolute_url = remove_after_last_slash(absolute_url)
            links.add(absolute_url)
    return links

# filters the URLs so that each page is on its "homepage" as many pages share target headers
def remove_after_last_slash(url): # removes all characters from the last forward slash to the end of the URL
    parsedURL = urlparse(url)
    path = parsedURL.path
    index = path.rfind('/') # index of the last forward slash character
    newPath = path[:index]
    modifiedURL = urlunparse(parsedURL._replace(path=newPath, fragment=''))
    return modifiedURL

def crawlerThread(frontier, num_targets):
    targets_found = 0

    while not frontier.done(): # while there are unvisited URLs in the Frontier
        url = frontier.nextURL()
        html = retrieveURL(url)

        if target_page(html):
            store_page(url, html) # I moved this line from the psuedocode
            targets_found += 1

        if targets_found == num_targets:
            frontier.clear()
        else:
            for unvisitedURL in parse(html, url): # url is inputted as the base url to absolute relative links
                frontier.addURL(unvisitedURL)

def target_page(html): # determines if page (URL) contains 6 classes of Default Header Section Pattern, also checking Department Name
    if html is None: # works with the error handling output from retrieveURL (HTTP Error 404, etc.)
        return False

    soup = BeautifulSoup(html, 'html.parser')
    classNames = ['fac-info', 'title-dept', 'emailicon', 'phoneicon', 'locationicon', 'hoursicon']

    for className in classNames:
        if not soup.find(class_=className):
            return False

    departmentName = "College of Business Administration"
    if departmentName in soup.find('span', class_='title-dept').get_text():
        return True

    return False