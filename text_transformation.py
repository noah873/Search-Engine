from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
from sklearn.base import BaseEstimator, TransformerMixin
from db_connection import connectDatabase
import nltk
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')

# Custom Stemmed CountVectorizer
class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        stemmer = PorterStemmer()
        return lambda doc: (stemmer.stem(token) for token in analyzer(doc))

# Tokenization using scikit-learn
def tokenize(text):
    vectorizer = CountVectorizer()
    analyzer = vectorizer.build_analyzer()
    return analyzer(text)

# Stop Words Removal using scikit-learn
def remove_stopwords(tokens):
    stop_words = ENGLISH_STOP_WORDS
    return [token for token in tokens if token.lower() not in stop_words]

# Stemming using scikit-learn's custom vectorizer
def stem_tokens(tokens):
    stemmed_vectorizer = StemmedCountVectorizer()
    stemmed_tokens = list(stemmed_vectorizer.build_analyzer()(" ".join(tokens)))
    return stemmed_tokens

# Full Text Transformation
def text_transformation(text):
    tokens = tokenize(text)
    filtered_tokens = remove_stopwords(tokens)
    stemmed_tokens = stem_tokens(filtered_tokens)
    return [token.lower() for token in stemmed_tokens if not any(char.isdigit() for char in token)]

def transformPages():
    db = connectDatabase()
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

# Test the functions (Optional)
if __name__ == "__main__":
    sample_text = "This is a sample sentence for tokenization, stopping, and stemming."
    transformed_text = text_transformation(sample_text)
    print(transformed_text)  # Output: ['sampl', 'sentenc', 'token', 'stop', 'stem']


