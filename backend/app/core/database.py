"""SQLAlchemy Database and Base Class Configuration."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Database connection URL, can be configured via environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user:password@db:5432/rl_campus_transport"
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Session class for interacting with the database
SessionLocal = sessionmaker(bind=engine)

# Base class for ORM models
Base = declarative_base()

def create_tables():
    """
    Creates all tables in the database that do not exist yet.
    
    IMPORTANT: Models are imported inside the function to avoid
    circular import issues.
    """
    # Import models here to avoid circular imports
    from app.models.user import User # pylint: disable=import-outside-toplevel,unused-import

    # Create all tables that inherit from Base
    Base.metadata.create_all(bind=engine)
