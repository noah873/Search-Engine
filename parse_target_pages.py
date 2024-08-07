from bs4 import BeautifulSoup, Comment

from db_connection import connectDatabase
db = connectDatabase()

def isVisible(text):  # function used by parseTargetPages(), returns True if text is visible, otherwise False
    if text.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(text, Comment):
        return False
    return True

def extractText(html): # function used by parseTargetPages()
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.findAll(text = True)  # creates array of text
    visibleText = filter(isVisible, text)  # filters text so only visible text remains
    return " ".join(text.strip() for text in visibleText)  # removes newline chars with split() and rejoins all visible text

def extractSections(soup, cssClass): # function used by parseTargetPages()
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

def parseTargetPages(): # extracts search areas from webpage and stores it in MongoDB db.target_pages
    targetPages = db.crawled_pages.find({"isTarget": True})

    for targetPage in targetPages:
        soup = BeautifulSoup(targetPage["html"], 'html.parser')
        blurbs = extractSections(soup, 'blurb') # blurbs are rows in the body (center column)
        accolades = extractSections(soup, 'accolades') # accolades are rows in the sidebar (right column)

        db.target_pages.insert_one({ # insert page into MongoDB db.target_pages
            "url": targetPage["url"],
            "body": blurbs,
            "sidebar": accolades
        })
        print(f"Parsed Target Page: '{targetPage["url"]}'")
