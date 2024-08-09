from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer # scikit-learn does not have a stemmer or lemmatizer

from db_connection import connectDatabase
db = connectDatabase()

stemmer = PorterStemmer()
vectorizer = CountVectorizer(stop_words = 'english')

def text_transformation(text):
    try:
        X = vectorizer.fit_transform([text]) # create a matrix of term counts
        tokenCounts = X.toarray().flatten()
        uniqueTokens = vectorizer.get_feature_names_out()

        tokens = [uniqueToken for uniqueToken, tokenCount in zip(uniqueTokens, tokenCounts) for i in range(tokenCount)] # create a list with duplicates

        stemmedTokens = [stemmer.stem(token) for token in tokens] # apply stemming

    except Exception as e:
        print(f"Error Transforming Text: '{text}', {e}")
        stemmedTokens = []

    return stemmedTokens

def transformPages():
    documents = db.target_pages.find()

    for document in documents:
        tokens = []

        for section in document['blurbs']:
            tokens += text_transformation(section['title'])
            tokens += text_transformation(section['text'])

        for section in document['accolades']:
            tokens += text_transformation(section['title'])
            tokens += text_transformation(section['text'])

        db.transformed_pages.insert_one({
            "url": document['url'],
            "tokens": tokens
        })
        print(f"Transformed Target Page: '{document['url']}'")
