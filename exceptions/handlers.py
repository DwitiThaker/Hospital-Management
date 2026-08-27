from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.medicine import (
    MedicineNotFoundError,
    InvalidMedicineIdError,
    EmptyMedicineUpdateError,
)


async def medicine_not_found_handler(
    request: Request,
    exc: MedicineNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


async def invalid_medicine_id_handler(
    request: Request,
    exc: InvalidMedicineIdError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


async def empty_medicine_update_handler(
    request: Request,
    exc: EmptyMedicineUpdateError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )
