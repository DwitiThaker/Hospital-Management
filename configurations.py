from pymongo import MongoClient #type: ignore
from pymongo.server_api import ServerApi  # type: ignore
from pymongo.collection import Collection  #type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("URI")

client = MongoClient(uri, server_api=ServerApi(SERVER_API))


db = client.hospital_db


user_collection: Collection = db["user"]
prescription_collection: Collection = db["prescriptions"]
medicine_collection: Collection = db["medicine"]  

def get_user_collection() -> Collection:
    return user_collection 

def get_prescription_collection() -> Collection:
    return prescription_collection

def get_medicine_collection() -> Collection:
    return medicine_collection
