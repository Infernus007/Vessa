"""VESSA Web Application Firewall.

This module provides the core WAF functionality for inline request protection.
"""

from .waf_engine import WAFEngine
from .waf_middleware import WAFMiddleware, create_waf_middleware
from .waf_config import WAFConfig
from .blocking_engine import BlockingEngine

__all__ = [
    'WAFEngine',
    'WAFMiddleware',
    'create_waf_middleware',
    'WAFConfig',
    'BlockingEngine'
]

