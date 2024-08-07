from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from db_connection import connectDatabase

db = connectDatabase()

# Tokenization
def tokenize(text):
    vectorizer = CountVectorizer()
    analyzer = vectorizer.build_analyzer()
    return analyzer(text)

# Stop Words Removal
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token.lower() not in stop_words]

# Stemming
def stem_tokens(tokens):
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

# Full Text Transformation
def text_transformation(text):
    tokens = tokenize(text)  # Tokenization
    tokens_without_stopwords = remove_stopwords(tokens)  # Stop words removal
    stemmed_tokens = stem_tokens(tokens_without_stopwords)  # Stemming
    return [token.lower() for token in stemmed_tokens if not any(char.isdigit() for char in token)]  # Convert to lowercase and remove numbers

def transformPages():
    documents = db.target_pages.find()

    for document in documents:
        blurbs = document['body']
        accolades = document['sidebar']

        # Transform the text before storing
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

