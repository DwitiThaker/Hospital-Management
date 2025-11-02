from fastapi import APIRouter, Depends, Body, HTTPException, status, Request
from typing import List
from pymongo.collection import Collection #type: ignore
from pymongo.errors import PyMongoError
from bson import ObjectId #type: ignore
from bson.errors import InvalidId #type: ignore
from datetime import datetime
import logging

from authentication import *
from MongoDB.schemas import *
from Services.user_services import *
from configurations import get_user_collection

logger = logging.getLogger(__name__)

def insert_doctor(doctor_user: UserCreate ,users_collection: Collection) -> UserOut:
    existing_user = get_user_by_email(doctor_user.email)
    if existing_user:
        logger.exception(f"register: email already exists")
        raise HTTPException(status_code=409, detail="email already exists")
    
    try:
        logger.info(f"create doctor: hashing the password...")
        hashed_pwd = hash_pwd(doctor_user.password)

    except ValueError as val_err:   
        logger.exception(f"register: Password hashing failed: {val_err}")
        raise HTTPException(status_code=500, detail="Password hashing failed")
    
    new_doctor_doc = {
        "username": doctor_user.username,
        "password": hashed_pwd,
        "email": doctor_user.email,
        "role": Role.doctor.value,
        "is_active": True
    }


    try:
        logger.info(f" Creating doctor...")
        result = users_collection.insert_one(new_doctor_doc)
        created_user = users_collection.find_one({"_id": result.inserted_id})

    except Exception as db_err:
        logger.exception(f"Failed to create doctor: {db_err}")
        raise HTTPException(status_code=500, detail="Failed to create doctor")

    if created_user:
            logging.info("User Created Successfully...")

            return UserOut(
                username=created_user['username'],
                email=created_user['email'],
                is_active=created_user['is_active'],
                role=Role.doctor
            )
            
    


def insert_nurse(nurse_user: UserCreate ,users_collection: Collection) -> UserOut:
    existing_user = get_user_by_email(nurse_user.email)
    if existing_user:
        logger.exception(f"register: email already exists")
        raise HTTPException(status_code=409, detail="email already exists")

    try:
        logger.info(f"create nurse: hashing the password...")
        hashed_pwd = hash_pwd(nurse_user.password)

    except ValueError as val_err:   
        logger.exception(f"register: Password hashing failed: {val_err}")
        raise HTTPException(status_code=500, detail="Password hashing failed")

    new_nurse_doc = {
        "username": nurse_user.username,
        "password": hashed_pwd,
        "email": nurse_user.email,
        "role": Role.nurse.value,
        "is_active": True
    }

    try:
        logger.info(f" Creating nurse...")
        result = users_collection.insert_one(new_nurse_doc)
        created_user = users_collection.find_one({"_id": result.inserted_id})

    except Exception as db_err:
        logger.exception(f"Failed to create nurse: {db_err}")
        raise HTTPException(status_code=500, detail="Failed to create nurse")

    if created_user:
            logging.info("User Created Successfully...")

            return UserOut(
                username=created_user['username'],
                email=created_user['email'],
                is_active=created_user['is_active'],
                role=Role.nurse
            )
            


def fetch_prescription(id: str, collect: Collection, medicine_collect: Collection):
    try:
        doctor_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    
    logger.info(f"Searching for doctor_id: {doctor_id}")
        
    try:
        docs = list(collect.find({"doctor_id": doctor_id}))
        
        logger.info(f"Found {len(docs)} prescriptions")
    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(db_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
    
    if not docs:
        raise HTTPException(status_code=404, detail="No prescriptions found for this doctor")
    
    prescription_list = []
    for doc in docs:
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
        
        prescription_list.append(ReadPrescription(**prescription_data))
    
    return prescription_list



def aggr_fetch_prescription(id: str, collect: Collection, medicine_collect: Collection):
    try:
        doctor_id = ObjectId(id)
    except InvalidId:
        logger.error(f"Invalid doctor ID received: {id}, error: {e}")
        raise HTTPException(status_code=400, detail="Invalid doctor ID format")
    
    logger.info(f"Searching for doctor_id: {doctor_id}")
        
    
    logger.info(f"Executing aggregation pipeline for doctor_id: {doctor_id}")

    pipeline = [
    {"$match": {"doctor_id": doctor_id}},
    {"$unwind": "$medicines"},
    {"$lookup": {
        "from": medicine_collect.name,
        "localField": "medicines.medicine_id",
        "foreignField": "medicine_id",
        "as": "medicine_details"
    }},
    {"$unwind": "$medicine_details"},
    {"$group": {
        "_id": "$_id",
        "doctor_id": {"$first": "$doctor_id"},
        "patient_id": {"$first": "$patient_id"},
        "patient_name": {"$first": "$patient_name"},
        "description": {"$first": "$description"},
        "completed": {"$first": "$completed"},
        "expiry": {"$first": "$expiry"},
        "created_at": {"$first": "$created_at"},
        "medicines": {"$push": {
            "medicine_id": "$medicine_details.medicine_id",
            "medicine_name": "$medicine_details.medicine_name",
            "quantity": "$medicines.quantity",
            "expiry": "$medicine_details.expiry",
            "created_at": "$medicine_details.created_at"
        }}
    }},
    {"$sort": { "created_at": -1 } } 
]

    logger.info(f"Aggregation returned {len(pipeline)} prescriptions")


    try:
        docs = list(collect.aggregate(pipeline))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if not docs:
        raise HTTPException(status_code=404, detail="No prescriptions found")
    
    
    prescription_list = [ReadPrescription(
        prescription_id=str(doc["_id"]),
        user_id=str(doc.get("patient_id", "")),
        patient_name=doc.get("patient_name", ""),
        description=doc.get("description", ""),
        completed=doc.get("completed", False),
        medicines=doc.get("medicines", []),
        expiry=doc.get("expiry"),
        created_at=doc.get("created_at")
    ) for doc in docs]
    
    return prescription_list



def fetch_doctors(collect: Collection) -> List[UserOut]:
    try:
        fetch = collect.find({"role": "doctor"})
        
    except Exception as db_err:
        logger.error(f"Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Database error occurred")

    if not fetch:
        raise HTTPException(status_code=404, detail="No doctors in the database")

    return [
        UserOut(
        username = f.get("username", ""),
        email = f.get("email", ""),
        is_active = f.get("is_active", False),
        role = f.get("role", ""),
        )
        for f in fetch
    ]


def fetch_nurses(collect: Collection) -> List[UserOut]:
    try:
        fetch = collect.find({"role": "nurse"})
    
    except Exception as db_err:
        logger.error(f"Database error: {db_err}")
        raise HTTPException(status_code=500, detail="Database Error Occured")
    
    if not fetch:
        raise HTTPException(status_code=404, detail="No nurses in the databse")
    
    return [
        UserOut(
        username = f.get("username", ""),
        email = f.get("email", ""),
        is_active = f.get("is_active", False),
        role = f.get("role", ""),
        )
        for f in fetch
    ]
    



def update_doctor_password(collect: Collection, password_data: PasswordUpdate, doctor_id: str) -> dict:
    try:
        doctor = user_collection.find_one({"_id": ObjectId(doctor_id)})
        if not doctor:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password_data.old_password, doctor["password"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not password_data.new_password or len(password_data.new_password.strip()) == 0:
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        
        logger.info(f"Updating password for doctor_id={doctor_id}")
        try:
            object_id = ObjectId(doctor_id)
        except Exception as e:
            logger.error(f"Invalid doctor ID format: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid doctor ID format: {e}")
        
        hashed_password = hash_pwd(password_data.new_password)
        
        result = collect.update_one(
            {"_id": object_id},
            {"$set": {"password": hashed_password}}
        )
        
        if result.matched_count == 0:
            logger.warning(f"Doctor not found for ID: {doctor_id}")
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        logger.info("Password updated successfully")
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        logger.error("Failed to update password ...")
        raise HTTPException(status_code=500, detail=f"Failed to update password due to server error {e}")


def update_nurse_password(collect: Collection, password_data: PasswordUpdate, nurse_id: str) -> dict:
    try:
        nurse = user_collection.find_one({"_id": ObjectId(nurse_id)})
        if not nurse:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password_data.old_password, nurse["password"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not password_data.new_password or len(password_data.new_password.strip()) == 0:
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        
        logger.info(f"Updating password for nurse_id={nurse_id}")
        try:
            object_id = ObjectId(nurse_id)
        except Exception as e:
            logger.error(f"Invalid nurse ID format: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid nurse ID format: {e}")
        
        hashed_password = hash_pwd(password_data.new_password)
        
        result = collect.update_one(
            {"_id": object_id},
            {"$set": {"password": hashed_password}}
        )
        
        if result.matched_count == 0:
            logger.warning(f"nurse not found for ID: {nurse_id}")
            raise HTTPException(status_code=404, detail="nurse Id not found")
        
        logger.info("Password updated successfully")
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        logger.error("Failed to update password ...")
        raise HTTPException(status_code=500, detail="Failed to update password due to server error")