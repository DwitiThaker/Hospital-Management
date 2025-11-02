from fastapi import APIRouter, status, HTTPException, Depends, Request
from pymongo.collection import Collection
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging
from typing import List
from pymongo.errors import PyMongoError
from datetime import datetime


from MongoDB.schemas import ReadMedicine, CreateMedicine, UpdateMedicine


logger = logging.getLogger(__name__)  



def fetch_all_medicines(nurse_id: str, collect: Collection) -> List[ReadMedicine]:
    try:
        nid = ObjectId(nurse_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Invalid Id Format")
    
    try:
        fetch = list(collect.find({"nurse_id": nid}))

    except PyMongoError as db_err:
        logger.error(f"read_all_medicine: Database error {db_err}")
        raise HTTPException(status_code=500, detail="Database error occurred:")
    except Exception as e:
        logger.error(f"read_all_medicine: An unexpected error occurred: {e}")

    if not fetch:
        raise HTTPException(status_code=400, detail="No medicine found in databse")
    
    return [
         ReadMedicine(
            medicine_id=str(f["_id"]),  
            medicine_name=f.get("medicine_name", ""),  # ← Change to medicine_name
            quantity=f.get("quantity"),
            expiry=f.get("expiry"),
            created_at=f.get("created_at")
)
        for f in fetch
    ]
    

def fetch_medicine(id: str, collect: Collection, nurse_id) -> ReadMedicine:
    try:
        object_id = ObjectId(id)
        nid = ObjectId(nurse_id)

    except InvalidId:
        raise HTTPException(status_code=404, detail="Invalid Id Format")
    
    try:
        doc = collect.find_one({"_id": object_id, "nurse_id": nid})
        if not doc:
            raise HTTPException(status_code=400, detail="No medicine found in database")
    except PyMongoError as db_err:
        logger.error(f"read_all_medicine: Database error {db_err}")
        raise HTTPException(status_code=500, detail="Database error occurred:")
    except Exception as e:
        logger.error(f"read_all_medicine: An unexpected error occurred: {e}")

        
        
    return ReadMedicine(
    medicine_id=str(doc["_id"]),  
    medicine_name=doc.get("medicine_name", ""),  # ← Change to medicine_name
    quantity=doc.get("quantity"),
    expiry=doc.get("expiry"),
    created_at=doc.get("created_at")
)


def new_medicine(new_medicine: CreateMedicine, collect: Collection, nurse_id) -> ReadMedicine:
    try:
        nid = ObjectId(nurse_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Id Format")
    
    try:
        logger.info("new_medicine: Adding new data.....")
        data = new_medicine.dict()
        
        data.update({
            "created_at": datetime.utcnow()  ,
            "nurse_id": nid
        })

        result = collect.insert_one(data)

        doc = collect.find_one({"_id": result.inserted_id})

    except PyMongoError as db_err:
        logger.error(f"Database error: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if not doc:
        logger.error("Failed to fetch created medicine")
        raise HTTPException(status_code=500, detail="Failed to fetch created medicine")

    return ReadMedicine(
    medicine_id=str(doc["_id"]),  
    medicine_name=doc.get("medicine_name", ""),  # ← Change to medicine_name
    quantity=doc.get("quantity"),
    expiry=doc.get("expiry"),
    created_at=doc.get("created_at")
)




def alter_medicine(id: str, alter_data: UpdateMedicine, collect: Collection, nurse_id: str) -> ReadMedicine:
    try:
        object_id = ObjectId(id)
        nid = ObjectId(nurse_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Id format")

    update_dict = {k: v for k, v in alter_data.dict(exclude_unset=True).items()}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    try:
        logger.info("alter_medicine: updating the dictionary.....")
        result = collect.update_one({"_id": object_id, "nurse_id": nid}, {"$set": update_dict})

    except PyMongoError as db_err:
        logger.exception(f"Database error during update: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
    except Exception as e:
        logger.exception(f"Unexpected error during update: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Medicine not found or not authorized")


    doc = collect.find_one({"_id": object_id, "nurse_id": nid})
    if not doc:
        raise HTTPException(status_code=404, detail="Medicine not found after update")

    logger.info("alter_medicine: Updated successfully")
    return ReadMedicine(
    medicine_id=str(doc["_id"]),  
    medicine_name=doc.get("medicine_name", ""),  # ← Change to medicine_name
    quantity=doc.get("quantity"),
    expiry=doc.get("expiry"),
    created_at=doc.get("created_at")
)



def remove_medicine(id: str, collect: Collection, nurse_id: str) -> dict:
    try:
        object_id = ObjectId(id)
        nid = ObjectId(nurse_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Id Format")
    
    try:
        result = collect.delete_one({"_id": object_id, "nurse_id": nid})
        
    except PyMongoError as db_err:
        logger.exception(f"Database error during medicine deletion: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
    except Exception as e:
        logger.exception(f"Unexpected error during medicine deletion: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    logger.info(f"remove_medicine: Medicine {id} deleted successfully")
    return {"message": "Medicine deleted successfully"}
