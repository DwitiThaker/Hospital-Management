from typing import Optional, List
from bson import ObjectId
from pymongo.collection import Collection


class MedicineRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, medicine_data: dict) -> dict:
        result = self.collection.insert_one(medicine_data)

        created_medicine = self.collection.find_one({"_id": result.inserted_id})

        if created_medicine is None:
            raise RuntimeError("Medicine was created but could not be retrieved")

        return created_medicine
    
    def get_by_id(self, medicine_id: ObjectId,) -> Optional[dict]:
        return self.collection.find_one({"_id": medicine_id})
    
    def get_all(self) -> List[dict]:
        return list(self.collection.find())
    
    def get_by_name(self, name:str) -> Optional[dict]:
        return self.collection.find_one({"name": name})
    
    def search(self, query: str) -> list[dict]:
        return list(self.collection.find({"name": {"$regex": query, "$options": "i"}}))
        
    def update(self, medicine_id: ObjectId, update_data: dict) -> Optional[dict]:
        result = self.collection.update_one({"_id": medicine_id}, {"$set": update_data})
        
        if result.matched_count == 0:
            return None
        
        return self.collection.find_one({"_id": medicine_id})
    
    def delete(self, medicine_id: ObjectId) -> bool:

        result = self.collection.delete_one({"_id": medicine_id})

        return result.deleted_count > 0
