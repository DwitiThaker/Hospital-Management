from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from MongoDB.models import Role


class Login(BaseModel):
    email: str
    password: str
    
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    is_active: bool = True


class UserOut(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    role: str

class MedicineItem(BaseModel):
    medicine_id: str
    quantity: int  

class MedicineReadItem(BaseModel):
    medicine_id: str
    medicine_name: str
    expiry: datetime
    quantity: int  

class CreatePrescription(BaseModel):
    patient_id: str
    patient_name: str
    description: str
    expiry: datetime
    medicines: List[MedicineItem] = Field(default_factory=list)  



class CreateMedicine(BaseModel):
    medicine_name: str
    expiry: datetime
    quantity: int

class ReadMedicine(BaseModel):
    medicine_name: Optional[str] = None
    quantity: int
    expiry: Optional[datetime] = None
    created_at: Optional[datetime] = None

class UpdateMedicine(BaseModel):
    medicine_name: Optional[str]  = None 
    quantity: int  = None 
    expiry: datetime  = None 
 

class PrescriptionOut(BaseModel):
    patient_id: str
    patient_name: str
    description: str
    expiry: datetime
    medicines: List[MedicineItem] = Field(default_factory=list)

class ReadPrescription(BaseModel):
    prescription_id: str
    user_id: str
    patient_name: str
    description: str
    completed: bool 
    medicines: List[ReadMedicine] = Field(default_factory=list)  
    expiry: datetime
    created_at: datetime


class UpdatePrescription(BaseModel):
    medicines: Optional[List[MedicineItem]] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class FetchforManager(BaseModel):
    prescription_id: str
    user_id: str
    patient_name: str
    description: str
    completed: bool 
    medicines: List[ReadMedicine] = Field(default_factory=list)  
    expiry: datetime
    created_at: datetime