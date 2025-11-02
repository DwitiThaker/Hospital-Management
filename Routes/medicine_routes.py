from fastapi import APIRouter, status, HTTPException, Depends, Request, Body
from pymongo.collection import Collection
from typing import List

from Services.medicine_services import *
from MongoDB.schemas import ReadMedicine, CreateMedicine, UpdateMedicine
from middleware import require_auth, require_role
from configurations import get_medicine_collection

medicine_router = APIRouter(    
    prefix="/nurse",
    tags=["nurse"]
)


@medicine_router.get("/read_all_medicines", response_model = List[ReadMedicine], status_code=status.HTTP_200_OK)
@require_role
@require_auth
async def read_all_medicines(
    request: Request,
    collection: Collection = Depends(get_medicine_collection)
):

    try:
        logger.info("Reading all medicine.........")
        nurse_id = request.state.user_id
        read_all = fetch_all_medicines(nurse_id, collection)
        return read_all

    except Exception as e:
        logger.error(f"reading_all_medicines: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@medicine_router.get("/read_medicine_by_id/{id}", response_model=ReadMedicine, status_code=status.HTTP_200_OK)
@require_role
@require_auth

async def read_medicine_by_id(
    request: Request,
    id: str, 
    collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Reading medicine.........")
        nurse_id = request.state.user_id
        read_all = fetch_medicine(id, collection, nurse_id)
        return read_all
    
    except Exception as e:
        logger.error(f"reading_medicine: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@medicine_router.post("/create_medicine", status_code=status.HTTP_201_CREATED)
@require_role
@require_auth
async def create_medicine(
    request: Request,
    create: CreateMedicine = Body(...), 
    collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Creating medicine.........")
        nurse_id = request.state.user_id
        created = new_medicine(create, collection, nurse_id)
        return created
    
    except Exception as e:
        logger.error(f"creating_medicine: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@medicine_router.put("/update_medicine_by_id/{id}", response_model=ReadMedicine, status_code=status.HTTP_200_OK)
@require_role
@require_auth
async def update_medicine_by_id(
    request: Request,
    id: str,
    update: UpdateMedicine = Body(...), 
    collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Updating medicine.........")
        nurse_id = request.state.user_id
        update = alter_medicine(id, update ,collection, nurse_id)
        return update
    
    except Exception as e:
        logger.error(f"updating_medicine: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@medicine_router.delete("/delete_medicine_by_id/{id}", response_model=ReadMedicine, status_code=status.HTTP_200_OK)
@require_role
@require_auth
async def delete_medicine_by_id(
    request: Request,
    collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Deleting medicine.........")
        nurse_id = request.state.user_id
        deleted = remove_medicine(id, deleted ,collection, nurse_id)
        return deleted      
    
    except Exception as e:
        logger.error(f"updating_medicine: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

