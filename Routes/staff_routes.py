from psycopg2 import DatabaseError
from pymongo.collection import Collection #type: ignore
from fastapi import APIRouter, Depends, Request, status, HTTPException


from authentication import *
from middleware import *
from Services.user_services import *
from Services.staff_services import *
from MongoDB.schemas import  UserOut, UserCreate
from configurations import get_medicine_collection, get_prescription_collection, get_user_collection

staff_router = APIRouter()


@staff_router.post("/management/create_doctor",  status_code=status.HTTP_200_OK, tags=["management"])
@require_role
async def create_doctor(
    request: Request,
    doctor: UserCreate
):

    try:
        added_doctor = insert_doctor(doctor, user_collection)
        return added_doctor
    except Exception as db_err:
            logger.exception(f"create_doctor: Failed to create doctor {db_err}")
            raise HTTPException(status_code=500, detail="Failed to create doctor")
    except Exception as e: 
            logger.exception(f"Unexpected error during creation: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")




@staff_router.post("/management/create_nurse",  status_code=status.HTTP_200_OK, tags=["management"])
@require_role
async def create_nurse(
    request: Request,
    nurse: UserCreate
):     
    try:
        added_nurse = insert_nurse(nurse, user_collection)
        return added_nurse
    except DatabaseError as db_err:  
        logger.exception(f"create_nurse: Failed to create nurse {db_err}")
        raise HTTPException(status_code=500, detail="Failed to create nurse")
    except Exception as e: 
        logger.exception(f"Unexpected error during creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@staff_router.get("/fetch_prescriptions_from_doctor_id/{doctor_id}", response_model=List[ReadPrescription], status_code=status.HTTP_200_OK, tags=["management"])
@require_auth
@require_role
async def fetch_prescriptions_from_doctor_id(
    request: Request,
    doctor_id: str,
    prescription_collection: Collection = Depends(get_prescription_collection),
    medicine_collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info(f"Endpoint called with doctor_id: {doctor_id}")  
        prescriptions = fetch_prescription(doctor_id, prescription_collection, medicine_collection)
        return prescriptions
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"fetch_all_prescriptions error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@staff_router.get("/fetch_pres_from_dr_arg/{doctor_id}", response_model=List[ReadPrescription], status_code=status.HTTP_200_OK, tags=["management"])
@require_auth
@require_role
async def agg_fetch_pres(
        request: Request,
        doctor_id: str,
        prescription_collection: Collection = Depends(get_prescription_collection),
        medicine_collection: Collection = Depends(get_medicine_collection)
):
    try:
        logger.info("Endpoint called with doctor_id: {doctor_id}")
        prescriptions = aggr_fetch_prescription(doctor_id, prescription_collection, medicine_collection)
        return prescriptions
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"fetch_all_prescriptions error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@staff_router.get("/read_all_doctors", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def read_all_doctors(
    user_collection: Collection = Depends(get_user_collection)
):
    try:
        read_all = fetch_doctors(user_collection)
        return read_all
    except Exception as e:
        logger.error(f"read_all_doctors: Internal issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@staff_router.get("/read_all_nurses", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def read_all_nurses(user_collection: Collection = Depends(get_user_collection)):
    try:
        read_all = fetch_nurses(user_collection)
        return read_all
    except Exception as e:
        logger.error(f"read_all_nurses: Internal Issue: {e}")
        raise HTTPException(status_code=500, detail="Internal Server error")
    

    

@staff_router.put("/doctor/change_doctor_password", status_code=status.HTTP_200_OK, tags=["doctor"])
@require_role
@require_auth
async def change_doctor_password(
    request: Request,  
    payload: PasswordUpdate,
    user_collection: Collection = Depends(get_user_collection)
):
    try:
        logger.info("Password change request received")

        doctor_id = request.state.user_id
        logger.info(f"doctor_id: {doctor_id}")
        if not doctor_id:
            logger.error("No user_id found in request state")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = update_doctor_password(
            collect=user_collection,
            password_data=payload,
            doctor_id=doctor_id
        )
        
        logger.info(f"Password change completed successfully for doctor_id={doctor_id}")
        return result
        
    except Exception as e:
        logger.error(f"change_doctor_password: Unexpected error..........: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@staff_router.put("/nurse/change_nurse_password", status_code=status.HTTP_200_OK, tags=["nurse"])
@require_role
@require_auth
async def change_nurse_password(
     request: Request, 
     payload: PasswordUpdate,
     user_collection: Collection = Depends(get_user_collection)
    ):
        try:
            logger.info("Password change request received")
            nurse_id = request.state.user_id
            if not nurse_id:
                logger.error("No user_id found in request state")
                raise HTTPException(status_code=401, detail="Authentication required")
        
            result = update_nurse_password(
            collect=user_collection,
            password_data=payload,
            nurse_id=nurse_id
        )
        
            logger.info(f"Password change completed successfully for nurse_id={nurse_id}")
            return result
        
        except Exception as e:
            logger.error(f"change_nurse_password: Unexpected error..........: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        
    