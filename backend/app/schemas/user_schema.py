"""Schemas de validacion para los usuarios de la API."""

from enum import Enum
from pydantic import BaseModel, EmailStr

# enum for role
class UserRole(str, Enum):
    """Enumeracion de roles posibles para los usuarios."""
    DRIVER = "driver"
    PASSENGER = "passenger"

# schema to serialize/validate users
class UserSchema(BaseModel): # pylint: disable=too-few-public-methods
    """Schema para crear un usuario mediante la API."""
    id: int
    first_name: str
    last_name: str
    dni: str
    email: EmailStr
    role: UserRole

    class Config: # pylint: disable=too-few-public-methods
        """COngiguracion interna para soportar SQLAlchemy ORM."""
        orm_mode = True  # allows you to receive SQLAlchemy objects directly
