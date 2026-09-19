from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from DB.models import Role
from enum import Enum

# class Login(BaseModel):
#     email: str
#     password: str


# class PasswordUpdate(BaseModel):
#     old_password: str
#     new_password: str


# class UserCreate(BaseModel):
#     username: str
#     password: str
#     email: EmailStr
#     is_active: bool = True


# class UserOut(BaseModel):
#     username: str
#     email: EmailStr
#     is_active: bool
#     role: str


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


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CreatePatient(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    gender: Gender
    phone: str = Field(min_length=10, max_length=15, pattern=r"^\d+$")
    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    emergency_contact: str = Field(min_length=10, max_length=15, pattern=r"^\d+$")


class ReadPatient(BaseModel):
    patient_id: str
    full_name: str
    date_of_birth: date
    gender: str
    phone: str

    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    emergency_contact: str | None = None

    created_at: datetime
    updated_at: datetime


class UpdatePatient(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    date_of_birth: date | None = None
    gender: Gender | None = None

    phone: str | None = Field(min_length=10, max_length=15, pattern=r"^\d+$")

    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    emergency_contact: str | None = None


class FetchforManager(BaseModel):
    prescription_id: str
    user_id: str
    patient_name: str
    description: str
    completed: bool
    medicines: List[ReadMedicine] = Field(default_factory=list)
    expiry: datetime
    created_at: datetime
