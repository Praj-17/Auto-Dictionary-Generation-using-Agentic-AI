from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["autodictionary_db"]
collection = db["words"]

# Insert a test word
collection.insert_one({"word": "testword2", "meaning": "This is a test 2nd time"})
print("✅ Test word inserted!")

# Check if it appears in MongoDB Compass
print(list(collection.find()))
