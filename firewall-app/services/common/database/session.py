"""Database session management.

This module provides database connection and session management functionality.
"""

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database configuration
DB_USER = os.getenv("DB_USER", "vessa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "vessa")

def get_database_url() -> str:
    """Get the database URL from environment variables.
    
    Returns:
        Database URL string
    """
    password = quote_plus(DB_PASSWORD)
    return f"mysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with MySQL-specific configuration
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,         # Enable connection health checks
    pool_size=5,               # Maximum number of connections to keep
    max_overflow=10,           # Maximum number of connections that can be created beyond pool_size
    pool_recycle=3600,        # Recycle connections after 1 hour
    connect_args={
        'connect_timeout': 30  # Connection timeout in seconds
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get a database session.
    
    Yields:
        Database session
        
    Note:
        This is a dependency that will be used by FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database.
    
    This function creates all tables in the database.
    It should be called when setting up the application.
    """
    from services.common.models.base import Base
    Base.metadata.create_all(bind=engine) 