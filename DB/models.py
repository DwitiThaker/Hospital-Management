from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    management = "management"
    doctor = "doctor"
    nurse = "nurse"


class Users(BaseModel):
    username: str
    password: str
    email: EmailStr   
    role: str = "management"
    is_active: bool = True


class Prescription(BaseModel):
    patient_name: str
    description: str
    qunatity: int
    completed: bool
    expiry: datetime
    created_at: datetime
    doctor_id: str

class Medicine(BaseModel):
    title: str
    qunatity: str
    expiry: datetime
    created_at: datetime 
