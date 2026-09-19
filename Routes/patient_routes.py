from fastapi import APIRouter, Depends, status

from Dependencies.patient import get_patient_service
from DB.schemas import CreatePatient, ReadPatient, UpdatePatient
from Services.patient_services import PatientService

patient_router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@patient_router.post(
    "/",
    response_model=ReadPatient,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient(
    data: CreatePatient,
    service: PatientService = Depends(get_patient_service),
):
    return await service.create_patient(data)


@patient_router.get(
    "/",
    response_model=list[ReadPatient],
)
async def get_all_patients(
    service: PatientService = Depends(get_patient_service),
):
    return await service.get_all_patients()


@patient_router.get(
    "/{patient_id}",
    response_model=ReadPatient,
)
async def get_patient_by_id(
    patient_id: str,
    service: PatientService = Depends(get_patient_service),
):
    return await service.get_patient_by_id(patient_id)


@patient_router.patch(
    "/{patient_id}",
    response_model=ReadPatient,
)
async def update_patient(
    patient_id: str,
    data: UpdatePatient,
    service: PatientService = Depends(get_patient_service),
):
    return await service.update_patient(
        patient_id,
        data,
    )


@patient_router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_patient(
    patient_id: str,
    service: PatientService = Depends(get_patient_service),
):
    await service.delete_patient(patient_id)
