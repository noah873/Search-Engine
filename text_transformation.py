import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Tokenization
def tokenize(text):
    return word_tokenize(text)

# Stop Words Removal
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return filtered_tokens

# Stemming
def stem_tokens(tokens):
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

# Full Text Transformation
def text_transformation(text):
    tokens = tokenize(text)
    filtered_tokens = remove_stopwords(tokens)
    stemmed_tokens = stem_tokens(filtered_tokens)
    return stemmed_tokens

def transformPages():
    from driver import connectDatabase  # enables connection to the shared MongoDB database
    db = connectDatabase()
    documents = db.pages.find()

    for document in documents:
        blurbs = document['body']
        accolades = document['sidebar']

        # Transform the text before storing
        for section in blurbs:
            section['text'] = text_transformation(section['text'])

        for section in accolades:
            section['text'] = text_transformation(section['text'])

        transformedDocument = {
            "url": document['url'],
            "body": blurbs,
            "sidebar": accolades
        }

        db.transformed_pages.insert_one(transformedDocument)

# Test the functions (Optional)
if __name__ == "__main__":
    sample_text = "This is a sample sentence for tokenization, stopping, and stemming."
    transformed_text = text_transformation(sample_text)
    print(transformed_text)
