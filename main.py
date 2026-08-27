from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from Routes import (
    staff_routes,
    user_routes,
    prescription_routes,
    medicine_routes,
)

from exceptions.handlers import (
    medicine_not_found_handler,
    invalid_medicine_id_handler,
    empty_medicine_update_handler,
)

from exceptions.medicine import (
    MedicineNotFoundError,
    InvalidMedicineIdError,
    EmptyMedicineUpdateError,
)


app = FastAPI()
router = APIRouter()


# Exception handlers
app.add_exception_handler(
    MedicineNotFoundError,
    medicine_not_found_handler,
)

app.add_exception_handler(
    InvalidMedicineIdError,
    invalid_medicine_id_handler,
)

app.add_exception_handler(
    EmptyMedicineUpdateError,
    empty_medicine_update_handler,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/home")
def home():
    return {"Successfull!"}


app.include_router(user_routes.user_auth_route)
app.include_router(prescription_routes.prescription_crud_route)
app.include_router(staff_routes.staff_router)
app.include_router(medicine_routes.medicine_router)
