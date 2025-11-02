from fastapi import APIRouter, Body, Depends, Request, HTTPException, status
from pymongo.collection import Collection #type: ignore
import logging


from MongoDB.schemas import CreatePrescription
from configurations import get_prescription_collection, get_medicine_collection
from Services.prescription_services import *
from middleware import require_auth, require_role

logger = logging.getLogger(__name__)

prescription_crud_route = APIRouter( 
    prefix="/doctor",
    tags=["doctor"]
    )


@prescription_crud_route.post("/create_prescription", status_code=status.HTTP_201_CREATED)
@require_auth     
@require_role  
async def create_prescription(
    request: Request,
    create: CreatePrescription = Body(...), 
    prescription_collection: Collection = Depends(get_prescription_collection),
    medicine_collection: Collection = Depends(get_medicine_collection)
):

    
    try:
        logger.info("Creating Prescription")
        user_id = request.state.user_id
        created_prescription = new_prescription(create, prescription_collection, user_id, medicine_collection)
        return created_prescription
    
    except Exception as e:
        logger.error(f"create_prescription: Internal issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


# @prescription_crud_route.get("/read_prescription_by_id/{id}", response_model=ReadPrescription ,status_code=status.HTTP_200_OK)
# @require_auth      
# @require_role  
# async def read_prescription_by_id(
#     request:Request,
#     id: str,
#     prescription_collection: Collection = Depends(get_prescription_collection)
# ):
#     try:
#         logger.info("Reading prescription....")
#         user_id = request.state.user_id
#         read_prescription = fetch_prescription_by_id(id, prescription_collection, user_id)
#         return read_prescription
    
#     except Exception as e:
#         logger.error(f"reading_prescription: Internal issue: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")     

@prescription_crud_route.get("/read_prescription_by_id/{id}", response_model=ReadPrescription, status_code=status.HTTP_200_OK)
@require_auth      
@require_role  
async def read_prescription_by_id(
    request: Request,
    id: str,
    prescription_collection: Collection = Depends(get_prescription_collection),
    medicine_collection: Collection = Depends(get_medicine_collection)  
):
    try:
        logger.info("Reading prescription....")
        user_id = request.state.user_id
        read_prescription = fetch_prescription_by_id(id, prescription_collection, medicine_collection, user_id)  
        return read_prescription
    
    except Exception as e:
        logger.error(f"reading_prescription: Internal issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@prescription_crud_route.get("/read_all_prescriptions", response_model=List[ReadPrescription], status_code=status.HTTP_200_OK, tags=["doctor"])
@require_auth     
@require_role  
async def read_all_prescriptions( request: Request, prescription_collection: Collection = Depends(get_prescription_collection)):
    
    try:
        logger.info("Reading all prescriptions....")
        user_id = request.state.user_id
        read_prescription = fetch_prescription(prescription_collection, user_id)
        return read_prescription
    
    except Exception as e:
        logger.error(f"reading_prescription: Internal issue: {e}")
        raise HTTPException(status_code=500, detail="Prescription not found")



@prescription_crud_route.put("/update_prescription_by_id/{id}", response_model=PrescriptionOut, status_code = status.HTTP_200_OK)
@require_auth      
@require_role  
async def update_prescription(
    request: Request,
    id: str,
    update_data: UpdatePrescription,
    prescription_collection: Collection = Depends(get_prescription_collection),
    medicine_collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Updating prescription.........")
        user_id = request.state.user_id
        update = alter_prescription(id, update_data ,prescription_collection, user_id, medicine_collection)
        return update
    
    except Exception as e:
        logger.error(f"updating_prescription: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@prescription_crud_route.delete("/delete_prescription_by_id/{id}",status_code= status.HTTP_200_OK)
@require_auth      # ← Changed order
@require_role  
async def delete_prescriptions(
    request: Request,
    id: str,
    prescription_collection: Collection = Depends(get_prescription_collection)
):
    
    try:
        logger.info("Deleting prescriptions..")
        user_id = request.state.user_id
        delete = remove_prescription(id, prescription_collection, user_id)
        return delete
    
    except Exception as e:
        logger.error(f"updating_prescription: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")