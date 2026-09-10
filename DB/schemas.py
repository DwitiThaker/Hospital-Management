from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from DB.models import Role


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


class CreateMedicine(BaseModel):
    name: str
    quantity: int = Field(ge=0)
    price: Decimal = Field(ge=0)
    expiry: date


class ReadMedicine(BaseModel):
    id: str
    name: str
    quantity: int
    price: Decimal
    expiry: date | None = None
    created_at: datetime
    updated_at: datetime


class UpdateMedicine(BaseModel):
    name: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    expiry: date | None = None


class CreatePrescription(BaseModel):
    patient_id: str
    patient_name: str
    description: str
    duration_days: int
    medicines: List[PrescriptionMedicine] = Field(default_factory=list)


class ReadPrescription(BaseModel):
    prescription_id: str
    doctor_id: str
    patient_id: str
    patient_name: str
    description: str
    medicines: List[PrescriptionMedicine] = Field(default_factory=list)
    duration_days: int
    issued_at: datetime
    updated_at: datetime


class UpdatePrescription(BaseModel):
    medicines: list[PrescriptionMedicine] | None = None
    description: str | None = None
    duration_days: int | None = Field(default=None, gt=0)


class PrescriptionMedicine(BaseModel):
    medicine_id: str
    quantity: int = Field(gt=0)


class FetchforManager(BaseModel):
    prescription_id: str
    user_id: str
    patient_name: str
    description: str
    completed: bool
    medicines: List[ReadMedicine] = Field(default_factory=list)
    expiry: datetime
    created_at: datetime
