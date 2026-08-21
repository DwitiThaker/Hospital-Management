import os

from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGO_URI = os.getenv("URI")

if not MONGO_URI:
    raise RuntimeError("MongoDB URI is not configured")

client = AsyncMongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
)

db = client["hospital_db"]

user_collection = db["user"]
prescription_collection = db["prescriptions"]
medicine_collection = db["medicine"]



