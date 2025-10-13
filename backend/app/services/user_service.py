"""Service layer for user-related operations."""

from app.models.user import User, UserRole
from werkzeug.security import generate_password_hash
from app.repositories.user_repository import UserRepository

class UserService:
    """Provides business logic for users."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self):
        """Return a list of users as dictionaries."""
        users = self.user_repository.get_all()
        return [self._serialize(user) for user in users]

    def get_user(self, user_id: int):
        """Return a single user by ID as dictionary or None if not found."""
        user = self.user_repository.get_by_id(user_id)
        if user:
            return self._serialize(user)
        return None

    def _serialize(self, user):
        """Convert a User model instance to a dictionary."""
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dni": user.dni,
            "email": user.email,
            "role": user.role.name
        }

    def create_user(self, first_name, last_name, dni, email, password, role):
        """Create and persist a new user."""
        # validate role
        if role not in UserRole._member_names_ and role not in [r.value for r in UserRole]:
            raise ValueError("Invalid role")

        # validate unique data
        existing_users = self.user_repository.get_all()
        if any(u.email == email for u in existing_users):
            raise ValueError("Email already registered")
        if any(u.dni == dni for u in existing_users):
            raise ValueError("DNI already registered")

        user = User(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            email=email,
            password_hash=generate_password_hash(password),
            role=UserRole(role) if isinstance(role, str) else role,
        )

        return self.user_repository.create(user)
