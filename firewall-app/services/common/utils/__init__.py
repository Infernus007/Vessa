"""Common utility functions."""

import uuid

def generate_uuid() -> str:
    """Generate a UUID string.
    
    Returns:
        str: A new UUID string
    """
    return str(uuid.uuid4()) 