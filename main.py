from fastapi import FastAPI, APIRouter

from Routes import staff_routes, user_routes, prescription_routes, medicine_routes



app = FastAPI()
router = APIRouter()


@app.get("/home")
def home():
    return {"Successfull!"}

app.include_router(user_routes.user_auth_route)
app.include_router(prescription_routes.prescription_crud_route)
app.include_router(staff_routes.staff_router)
app.include_router(medicine_routes.medicine_router)