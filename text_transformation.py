from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer

from db_connection import connectDatabase
db = connectDatabase()

lemmatizer = WordNetLemmatizer()
vectorizer = CountVectorizer(stop_words='english')

def text_transformation(text):
    try:
        vectorizer.fit_transform([text])
        tokens = vectorizer.get_feature_names_out()
        lemmatizedTokens = [lemmatizer.lemmatize(token) for token in tokens]
    except Exception as e:
        lemmatizedTokens = []

    return lemmatizedTokens

def transformPages():
    documents = db.target_pages.find()

    for document in documents:
        blurbs = document['body']
        accolades = document['sidebar']

        for section in blurbs:
            section['title'] = text_transformation(section['title'])
            section['text'] = text_transformation(section['text'])

        for section in accolades:
            section['title'] = text_transformation(section['title'])
            section['text'] = text_transformation(section['text'])

        transformedDocument = {
            "url": document['url'],
            "body": blurbs,
            "sidebar": accolades
        }

        db.transformed_pages.insert_one(transformedDocument)
        print(f"Transformed Target Page: '{document['url']}'")