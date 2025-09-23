from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
import enum

from core.database import Base

class UserRole(enum.Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), nullable=False)

    last_login = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)

    def __repr__(self): #defines how an object is represented as a string 
        return (
            f"<User(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}', role='{self.role.name}')>"
        )
