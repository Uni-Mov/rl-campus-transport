import enum
from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base

class UserRole(enum.Enum):
    """Enumeracion de roles posibles para los usuarios."""
    DRIVER = "driver"
    PASSENGER = "passenger"

class User(Base):
    """Representa un Usuario en la base de datos."""

    __tablename__ = "users" #Esto es para probar Pylint #2


    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dni = Column(String(10), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    def full_name(self):
        """Devuelve el Nombre Completo de usuario."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self): #defines how an object is represented as a string
        return (
            f"<User(id={self.id}, "
            f"name='{self.first_name} {self.last_name}', "
            f"email='{self.email}', role='{self.role.name}')>"
        )
