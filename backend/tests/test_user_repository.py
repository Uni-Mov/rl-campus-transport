import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_repository_get_all(in_memory_db):
    """Test get_all returns all users"""
    user = User(
        first_name="Test",
        last_name="User",
        dni="11111111",
        email="test@example.com",
        password_hash="pw",
        role=UserRole.DRIVER
    )
    in_memory_db.add(user)
    in_memory_db.commit()
    
    repo = UserRepository(in_memory_db)
    users = repo.get_all()
    assert len(users) == 1
    assert users[0].email == "test@example.com"

def test_user_repository_get_by_id(in_memory_db):
    """Test get_by_id returns the correct user"""
    user = User(
        first_name="Test",
        last_name="User",
        dni="11111111",
        email="test@example.com",
        password_hash="pw",
        role=UserRole.DRIVER
    )
    in_memory_db.add(user)
    in_memory_db.commit()
    
    repo = UserRepository(in_memory_db)
    fetched = repo.get_by_id(user.id)
    assert fetched.email == "test@example.com"
