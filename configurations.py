from pymongo.collection import Collection  

from DB.mongodb import (
    user_collection,
    prescription_collection,
    medicine_collection,
)

def get_user_collection() -> Collection:
    return user_collection 

def get_prescription_collection() -> Collection:
    return prescription_collection

def get_medicine_collection() -> Collection:
    return medicine_collection
