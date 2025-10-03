""" 
Defines the User model and roles for the application. 
This module includes the SQLAlchemy ORM mapping for users, 
with attributes such as name, DNI, email, password hash, and role. 
"""
import enum
from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base

class UserRole(enum.Enum):
    """Possible roles for users"""
    DRIVER = "driver"
    PASSENGER = "passenger"

class User(Base):
    """Represents a user in the database."""

    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dni = Column(String(10), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Defines how an object is represented as a string"""
        return (
            f"<User(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}', role='{self.role.name}')>"
        )
