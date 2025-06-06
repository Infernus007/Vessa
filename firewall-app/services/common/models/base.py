"""Base model configuration.

This module provides the base SQLAlchemy model configuration.
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr

class CustomBase:
    """Custom base class for all models."""
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name automatically."""
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase) 