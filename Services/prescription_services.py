from fastapi import APIRouter, Depends, Body, HTTPException, status, Request
from typing import List
from pymongo.collection import Collection #type: ignore
from pymongo.errors import PyMongoError
from bson import ObjectId #type: ignore
from bson.errors import InvalidId #type: ignore
from datetime import datetime
import logging

from MongoDB.schemas import *
from configurations import get_prescription_collection


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def update_medicine_stock(medicine_collect: Collection, medicine_id: ObjectId, delta_qty: int):
    try:
        result = medicine_collect.update_one(
            {"_id": medicine_id},
            {"$inc": {"quantity": -delta_qty}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Medicine with id {medicine_id} not found")
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error updating stock: {db_err}")


def adjust_medicine_stock(medicine_collect: Collection, old_meds: list, new_meds: list):
    old_dict = {str(m["medicine_id"]): m for m in old_meds}
    new_dict = {str(m["medicine_id"]): m for m in new_meds}

    all_ids = set(old_dict.keys()) | set(new_dict.keys())

    for med_id_str in all_ids:
        med_id = ObjectId(med_id_str)
        old_qty = old_dict.get(med_id_str, {}).get("quantity", 0)
        new_qty = new_dict.get(med_id_str, {}).get("quantity", 0)

        delta_qty = new_qty - old_qty
        if delta_qty != 0:
            update_medicine_stock(medicine_collect, med_id, delta_qty)



def new_prescription( new_prescription: CreatePrescription, collect: Collection, user_id: str, medicine_collect: Collection) -> PrescriptionOut:
    try:
        uid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Id format")

    medicine_list = []
    for item in new_prescription.medicines:
        try:
            med_id = ObjectId(item.medicine_id)  
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"Invalid medicine ID: {item.medicine_id}")

        med = medicine_collect.find_one({"_id": med_id})
        if not med:
            raise HTTPException(status_code=404, detail=f"Medicine with ID {item.medicine_id} not found")

        available_qty = int(med.get("quantity", 0))
        if item.quantity > available_qty:
            raise HTTPException(
                status_code=409,
                detail=f"{med.get('medicine_name', 'Unknown')} low stock. Available: {available_qty}"
            )

        medicine_list.append({
            "medicine_id": str(med["_id"]),
            "quantity": item.quantity
        })

    data = new_prescription.dict()
    data.update({
        "medicines": medicine_list,
        "completed": False,
        "created_at": datetime.utcnow(),
        "doctor_id": uid,
    })

    try:
        result = collect.insert_one(data)

        for m in medicine_list:
            update_medicine_stock(medicine_collect, ObjectId(m["medicine_id"]), m["quantity"])

        doc = collect.find_one({"_id": result.inserted_id})
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error: {db_err}")

    if not doc:
        raise HTTPException(status_code=500, detail="Failed to create prescription")

    return PrescriptionOut(**doc)



# def fetch_prescription_by_id( id: str, collect: Collection, user_id: str) -> ReadPrescription:
#     try:
#         uid = ObjectId(user_id)
#         object_id = ObjectId(id)
#     except InvalidId:
#         raise HTTPException(status_code=400, detail="Invalid ID format")

#     try:
#         doc = collect.find_one({"_id": object_id, "doctor_id": uid})
#     except PyMongoError as db_err:
#         raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

#     if not doc:
#         raise HTTPException(status_code=404, detail="Prescription not found")


#     doc["prescription_id"] = str(doc["_id"])
#     doc["user_id"] = str(doc["doctor_id"])

#     return ReadPrescription(**doc)

def fetch_prescription_by_id(id: str, collect: Collection, medicine_collect: Collection, user_id: str) -> ReadPrescription:
    try:
        uid = ObjectId(user_id)
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        doc = collect.find_one({"_id": object_id, "doctor_id": uid})
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if not doc:
        raise HTTPException(status_code=404, detail="Prescription not found")

    medicines_with_details = []
    for med in doc.get("medicines", []):
        try:
            med_id = ObjectId(med.get("medicine_id"))
            medicine_doc = medicine_collect.find_one({"_id": med_id})
            
            if medicine_doc:
                medicines_with_details.append({
                    "medicine_name": medicine_doc.get("medicine_name"),
                    "quantity": med.get("quantity"),
                    "expiry": medicine_doc.get("expiry"),
                    "created_at": medicine_doc.get("created_at")
                })
            else:
                logger.warning(f"Medicine with ID {med_id} not found")
        except (InvalidId, KeyError, TypeError) as e:
            logger.warning(f"Error processing medicine: {e}")
            continue

    prescription_data = {
        "prescription_id": str(doc["_id"]),
        "user_id": str(doc.get("patient_id", "")),
        "patient_name": doc.get("patient_name", ""),
        "description": doc.get("description", ""),
        "completed": doc.get("completed", False),
        "medicines": medicines_with_details,
        "expiry": doc.get("expiry"),
        "created_at": doc.get("created_at")
    }

    return ReadPrescription(**prescription_data)




def fetch_prescription(collect: Collection, user_id: str) -> List[ReadPrescription]:
    try:
        uid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        cursor = collect.find({"doctor_id": uid})
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")

    prescriptions = []

    for doc in cursor:
        doc["prescription_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["doctor_id"])
        doc["medicines"] = doc.get("medicines") or []

        try:
            prescriptions.append(ReadPrescription(**doc))
        except Exception as e:
            continue

    if not prescriptions:
        raise HTTPException(status_code=404, detail="Prescriptions not found")

    return prescriptions




def alter_prescription(id: str, alter_data: UpdatePrescription, collect: Collection, user_id: str, medicine_collect: Collection) -> PrescriptionOut:
    try:
        object_id = ObjectId(id)
        uid = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Id format")

    existing_prescription = collect.find_one({"_id": object_id, "doctor_id": uid})
    if not existing_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found or not authorized")

    update_dict = {k: v for k, v in alter_data.dict(exclude_unset=True).items()}

    if "medicines" in update_dict:
        new_meds = update_dict["medicines"]
        old_meds = existing_prescription.get("medicines", [])
        adjust_medicine_stock(medicine_collect, old_meds, new_meds)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")

    try:
        collect.update_one({"_id": object_id, "doctor_id": uid}, {"$set": update_dict})
        doc = collect.find_one({"_id": object_id, "doctor_id": uid})
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")

    if not doc:
        raise HTTPException(status_code=404, detail="Prescription not found after update")

    return PrescriptionOut(**doc)


    

def remove_prescription(id: str, collect: Collection, user_id: str) -> dict:
    try:
        object_id = ObjectId(id)
        uid = ObjectId(user_id)
    
    except InvalidId:
        raise HTTPException(status_code=400,  detail="Invalid Id Format")

    try:
        doc = collect.delete_one({"_id": object_id, "doctor_id": uid})

    except PyMongoError as db_err:
        logger.exception(f"Database error during Prescription update: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error occurred: {db_err}")
    except Exception as e:
        logger.exception(f"Unexpected error during Prescription update: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    
    if doc.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Prescription not found")
    
    logger.info(f"remove_prescription: Prescription {id} deleted successfully")
    return {"message": "Prescription deleted successfully"}
    


