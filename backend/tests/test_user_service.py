import pytest
from app.services.user_service import UserService
from app.models.user import User, UserRole

class FakeUserRepo:
    """Fake repository for testing service layer"""
    def get_all(self):
        return [
            User(
                id=1,
                first_name="Alice",
                last_name="Smith",
                dni="1234",
                email="alice@example.com",
                password_hash="pw",
                role=UserRole.DRIVER
            )
        ]
    def get_by_id(self, user_id):
        if user_id == 1:
            return User(
                id=1,
                first_name="Alice",
                last_name="Smith",
                dni="1234",
                email="alice@example.com",
                password_hash="pw",
                role=UserRole.DRIVER
            )
        return None

@pytest.fixture
def user_service():
    return UserService(FakeUserRepo())

def test_list_users(user_service):
    users = user_service.list_users()
    assert len(users) == 1
    assert users[0]["first_name"] == "Alice"

def test_get_user_found(user_service):
    user = user_service.get_user(1)
    assert user["email"] == "alice@example.com"

def test_get_user_not_found(user_service):
    user = user_service.get_user(999)
    assert user is None
