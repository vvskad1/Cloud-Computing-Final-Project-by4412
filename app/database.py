"""
Database configuration and session management for FixIt Tech Solutions.
Supports both SQLite (for development) and PostgreSQL (for production).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Determine database URL
# Default to SQLite if no DATABASE_URL is provided
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./fixit_tech.db"

# SQLite specific configuration
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI endpoints to get a database session.
    
    Usage:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    This should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
