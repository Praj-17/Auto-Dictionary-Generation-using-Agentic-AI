from pymongo import MongoClient
import os

# ✅ Connect to MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["autodictionary_db"]
collection = db["words"]

def save_word(word, meaning):
    """Save word and meaning to MongoDB without checking for duplicates."""
    try:
        collection.insert_one({"word": word, "meaning": meaning})
        print(f"✅ Word '{word}' saved to database.")
    except Exception as e:
        print(f"❌ Error saving word '{word}': {e}")



def get_all_words():
    """Retrieve all stored words from MongoDB."""
    return list(collection.find({}, {"_id": 0}))  # Exclude MongoDB `_id` field

def search_word(word):
    """Search for a specific word in MongoDB."""
    return collection.find_one({"word": word}, {"_id": 0})
