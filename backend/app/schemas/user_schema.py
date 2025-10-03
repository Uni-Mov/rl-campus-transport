"""Validation schemas for the API users."""

from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    """Enumeration of possible roles for users."""
    DRIVER = "driver"
    PASSENGER = "passenger"


class UserSchema(BaseModel):  # pylint: disable=too-few-public-methods
    """Schema used to create or serialize a user through the API."""
    id: int
    first_name: str
    last_name: str
    dni: str
    email: EmailStr
    role: UserRole

    class Config:  # pylint: disable=too-few-public-methods
        """Internal configuration to support SQLAlchemy ORM integration."""
        orm_mode = True  # allows reading SQLAlchemy model instances directly
