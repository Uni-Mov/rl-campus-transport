"""Service layer for user-related operations."""

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
