from fastapi import APIRouter, Depends, Request
from bson import ObjectId

from DB.schemas import (
    CreatePrescription,
    ReadPrescription,
    UpdatePrescription,
)
from Services.prescription_services import PrescriptionService
from Dependencies.prescription import get_prescription_service

prescription_router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@prescription_router.get(
    "/",
    response_model=list[ReadPrescription],
    status_code=200,
)
async def list_prescriptions(
    service: PrescriptionService = Depends(get_prescription_service),
):
    return await service.list_prescriptions()


@prescription_router.get(
    "/{prescription_id}",
    response_model=ReadPrescription,
    status_code=200,
)
async def get_prescription(
    prescription_id: str,
    service: PrescriptionService = Depends(get_prescription_service),
):
    return await service.get_prescription(prescription_id)


@prescription_router.post(
    "/",
    response_model=ReadPrescription,
    status_code=201,
)
async def create_prescription(
    data: CreatePrescription,
    request: Request,
    service: PrescriptionService = Depends(get_prescription_service),
):
    # TODO: Replace temporary doctor_id with authenticated user's ObjectId

    doctor_id = ObjectId()

    return await service.create_prescription(
        data,
        doctor_id,
    )


@prescription_router.patch(
    "/{prescription_id}",
    response_model=ReadPrescription,
    status_code=200,
)
async def update_prescription(
    prescription_id: str,
    data: UpdatePrescription,
    service: PrescriptionService = Depends(get_prescription_service),
):
    return await service.update_prescription(
        prescription_id,
        data,
    )


@prescription_router.delete(
    "/{prescription_id}",
    status_code=204,
)
async def delete_prescription(
    prescription_id: str,
    service: PrescriptionService = Depends(get_prescription_service),
):
    await service.delete_prescription(prescription_id)
