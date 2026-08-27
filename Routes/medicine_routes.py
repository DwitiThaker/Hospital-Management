from fastapi import APIRouter, Depends, status

from Dependencies.medicine import get_medicine_service
from MongoDB.schemas import CreateMedicine, ReadMedicine, UpdateMedicine
from Services.medicine_services import MedicineService


medicine_router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"],
)


@medicine_router.get(
    "/",
    response_model=list[ReadMedicine],
    status_code=status.HTTP_200_OK,
)
async def list_medicines(
    service: MedicineService = Depends(get_medicine_service),
):
    return await service.list_medicines()


@medicine_router.get(
    "/{medicine_id}",
    response_model=ReadMedicine,
    status_code=status.HTTP_200_OK,
)
async def get_medicine(
    medicine_id: str,
    service: MedicineService = Depends(get_medicine_service),
):
    return await service.get_medicine(medicine_id)


@medicine_router.post(
    "/",
    response_model=ReadMedicine,
    status_code=status.HTTP_201_CREATED,
)
async def create_medicine(
    data: CreateMedicine,
    service: MedicineService = Depends(get_medicine_service),
):
    return await service.create_medicine(data)


@medicine_router.patch(
    "/{medicine_id}",
    response_model=ReadMedicine,
    status_code=status.HTTP_200_OK,
)
async def update_medicine(
    medicine_id: str,
    data: UpdateMedicine,
    service: MedicineService = Depends(get_medicine_service),
):
    return await service.update_medicine(
        medicine_id,
        data,
    )


@medicine_router.delete(
    "/{medicine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medicine(
    medicine_id: str,
    service: MedicineService = Depends(get_medicine_service),
):
    await service.delete_medicine(medicine_id)
