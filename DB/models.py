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
