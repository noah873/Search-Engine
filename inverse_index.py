from collections import Counter

from db_connection import connectDatabase
db = connectDatabase()

def createInverseIndex():
    pages = db.transformed_pages.find()

    for page in pages:
        termCounts = Counter(page['tokens'])

        for term, frequency in termCounts.items():
            db.inverse_index.update_one(
                {'term': term},
                {'$push': {
                    'postings': {
                        'doc_id': page['_id'],
                        'frequency': frequency
                    }
                }},
                upsert = True
            )