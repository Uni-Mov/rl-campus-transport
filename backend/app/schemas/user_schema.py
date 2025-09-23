from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime


# enum for role 
class UserRole(str, Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"

# schema to serialize/validate users 
class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    dni: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True  # allows you to receive SQLAlchemy objects directly
