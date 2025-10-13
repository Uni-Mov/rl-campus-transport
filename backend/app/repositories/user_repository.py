"""Repository layer for User model. Handles database access."""

from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    """Provides database operations for User."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all(self):
        """Return all users from the database."""
        return self.db_session.query(User).all()

    def get_by_id(self, user_id: int):
        """Return a user by ID or None if not found."""
        return self.db_session.query(User).filter(User.id == user_id).first()

    def create(self, user: User):
        """Add a new user to the database."""
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
