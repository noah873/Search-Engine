import nltk
import string

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from db_connection import connectDatabase
db = connectDatabase()

# Tokenization
def tokenize(text):
    return word_tokenize(text)

# Stop Words Removal
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return filtered_tokens

# Lemmatization
def lemmatize_tokens(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens

# Remove Punctuation and Quotes
def remove_punctuation_and_quotes(tokens):
    table = str.maketrans('', '', string.punctuation + '“”’‘"—–-')
    stripped_tokens = [token.translate(table) for token in tokens]
    return [token for token in stripped_tokens if token]

# Full Text Transformation
def text_transformation(text):
    tokens = tokenize(text)
    tokens = remove_punctuation_and_quotes(tokens)  
    filtered_tokens = remove_stopwords(tokens)
    lemmatized_tokens = lemmatize_tokens(filtered_tokens)
    return [token.lower() for token in lemmatized_tokens if not any(char.isdigit() for char in token)]

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
    print(transformed_text)

