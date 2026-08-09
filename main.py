from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware  # Add this import

from Routes import staff_routes, user_routes, prescription_routes, medicine_routes

app = FastAPI()
router = APIRouter()

# Add CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/home")
def home():
    return {"Successfull!"}

app.include_router(user_routes.user_auth_route)
app.include_router(prescription_routes.prescription_crud_route)
app.include_router(staff_routes.staff_router)
app.include_router(medicine_routes.medicine_router)