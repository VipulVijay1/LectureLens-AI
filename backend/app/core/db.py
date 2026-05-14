from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)

database = client["lecturelens"]

# collections
video_status_collection = database["video_status"]
notes_collection = database["notes"]
flashcards_collection = database["flashcards"]

# backward compatibility
db = video_status_collection