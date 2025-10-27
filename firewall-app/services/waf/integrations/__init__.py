"""WAF Integrations for popular frameworks.

This module provides easy-to-use integrations for:
- Flask
- Django
- Express.js (via examples)
- Spring Boot (via examples)
"""

from .flask_integration import FlaskWAF
from .wsgi_integration import WSGIWAFMiddleware

__all__ = ['FlaskWAF', 'WSGIWAFMiddleware']

