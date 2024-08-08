from sklearn.feature_extraction.text import TfidfVectorizer
from db_connection import connectDatabase

# Connect to the database
db = connectDatabase()

def create_index():
    # Retrieve transformed target pages
    transformed_pages = db.transformed_pages.find()

    # Extract and transform text data
    corpus = []
    urls = []
    for page in transformed_pages:
        url = page['url']

        # Extracting and combining all transformed text content from body and sidebar
        faculty_info = []
        for section in page['blurbs']:
            faculty_info.extend(section['title'])
            faculty_info.extend(section['text'])
        for section in page['accolades']:
            faculty_info.extend(section['title'])
            faculty_info.extend(section['text'])

        transformed_faculty_info = " ".join(faculty_info)

        corpus.append(transformed_faculty_info)
        urls.append(url)

    # Create TF-IDF vectorizer and fit_transform on corpus
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)

    # Save the TF-IDF matrix and feature names to MongoDB
    db.index_data.insert_one({
        "tfidf_matrix": X.toarray().tolist(),
        "feature_names": vectorizer.get_feature_names_out().tolist(),
        "urls": urls
    })

    print(f"Created TF-IDF Matrix with shape: {X.shape}")
    print("Index data stored in MongoDB")

if __name__ == "__main__":
    create_index()
