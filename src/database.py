from pymongo import MongoClient
import os

# ✅ Connect to MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["autodictionary_db"]
collection = db["words"]

def save_word(word_data):
    """ Save a word and its definition to MongoDB. """
    if isinstance(word_data, dict) and "word" in word_data:
        # Ensure 'definition' exists before saving
        word_data["definition"] = word_data.get("definition", "No definition available")

        existing_entry = collection.find_one({"word": word_data["word"]})

        if existing_entry:
            print(f"⚠️ Word '{word_data['word']}' already exists in the database. Skipping.")
        else:
            collection.insert_one(word_data)
            print(f"✅ Word '{word_data['word']}' successfully saved.")

def get_all_words():
    """ Retrieves all words stored in the database. """
    return list(collection.find({}, {"_id": 0}))  # Exclude `_id`

def search_word(word):
    """ Searches for a specific word in the database. """
    return collection.find_one({"word": word}, {"_id": 0})  # ✅ Ensure `_id` is excluded