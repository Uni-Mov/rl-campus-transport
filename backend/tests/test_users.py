import pytest
from app.models.user import User, UserRole as ORMUserRole
from app.schemas.user_schema import UserSchema, UserRole as SchemaUserRole


def test_user_repr():
    """Verify that the __repr__ of the user model works correctly"""
    user = User(
        id=1,
        first_name="Juan",
        last_name="Perez",
        dni="12345678",
        email="juan@gmail.com",
        password_hash="hashed_pw",
        role=ORMUserRole.DRIVER,
    )
    repr_str = repr(user)
    assert "Juan Perez" in repr_str
    assert "juan@gmail.com" in repr_str
    assert "DRIVER" in repr_str


def test_user_schema_from_dict():
    """Validates that the Pydantic schema works with valid data"""
    data = {
        "id": 1,
        "first_name": "Juan",
        "last_name": "Perez",
        "dni": "12345678",
        "email": "juan@gmail.com",
        "role": "passenger",
    }
    user_schema = UserSchema(**data) # **data unpacks the dictionary as named arguments
    assert user_schema.first_name == "Juan"
    assert user_schema.role == SchemaUserRole.PASSENGER

