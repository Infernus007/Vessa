"""Structured Logging Configuration.

This module provides structured logging for better monitoring and debugging.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logs."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add module and function name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add process and thread info
        log_record['process'] = record.process
        log_record['thread'] = record.thread
        
        # Add application name
        log_record['application'] = 'vessa-firewall'


class StructuredLogger:
    """Structured logger for centralized monitoring."""
    
    def __init__(self, name: str):
        """Initialize structured logger.
        
        Args:
            name: Logger name (usually __name__)
        """
        self.logger = logging.getLogger(name)
        
        # Only configure if not already configured
        if not self.logger.handlers:
            self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger with structured JSON output."""
        # Set log level from environment or default to INFO
        import os
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Use JSON formatter for production
        if os.getenv('ENVIRONMENT', 'development') == 'production':
            formatter = CustomJsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s'
            )
        else:
            # Use readable format for development
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)
    
    # Security-specific logging methods
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **additional_context
    ):
        """Log security event.
        
        Args:
            event_type: Type of security event
            severity: critical, high, medium, low
            description: Event description
            user_id: User ID if applicable
            ip_address: IP address if applicable
            **additional_context: Additional context data
        """
        self.logger.warning(
            f"SECURITY: {event_type} - {description}",
            extra={
                'event_type': 'security',
                'security_event': event_type,
                'severity': severity,
                'user_id': user_id,
                'ip_address': ip_address,
                **additional_context
            }
        )
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **additional_context
    ):
        """Log API request.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: User ID if authenticated
            ip_address: Client IP address
            **additional_context: Additional context data
        """
        self.logger.info(
            f"API {method} {path} {status_code} {duration_ms}ms",
            extra={
                'event_type': 'api_request',
                'http_method': method,
                'http_path': path,
                'http_status': status_code,
                'duration_ms': duration_ms,
                'user_id': user_id,
                'ip_address': ip_address,
                **additional_context
            }
        )
    
    def log_database_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
        **additional_context
    ):
        """Log database query.
        
        Args:
            query_type: SELECT, INSERT, UPDATE, DELETE
            table: Table name
            duration_ms: Query duration in milliseconds
            rows_affected: Number of rows affected
            **additional_context: Additional context data
        """
        self.logger.debug(
            f"DB {query_type} {table} {duration_ms}ms",
            extra={
                'event_type': 'database_query',
                'query_type': query_type,
                'table': table,
                'duration_ms': duration_ms,
                'rows_affected': rows_affected,
                **additional_context
            }
        )
    
    def log_threat_detected(
        self,
        threat_type: str,
        severity: str,
        source_ip: str,
        confidence: float,
        **additional_context
    ):
        """Log threat detection.
        
        Args:
            threat_type: Type of threat
            severity: critical, high, medium, low
            source_ip: Source IP address
            confidence: Confidence score (0-1)
            **additional_context: Additional context data
        """
        self.logger.warning(
            f"THREAT: {threat_type} from {source_ip} (confidence: {confidence})",
            extra={
                'event_type': 'threat_detected',
                'threat_type': threat_type,
                'severity': severity,
                'source_ip': source_ip,
                'confidence': confidence,
                **additional_context
            }
        )
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        **additional_context
    ):
        """Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            **additional_context: Additional context data
        """
        self.logger.info(
            f"METRIC: {metric_name}={value}{unit}",
            extra={
                'event_type': 'performance_metric',
                'metric_name': metric_name,
                'metric_value': value,
                'metric_unit': unit,
                **additional_context
            }
        )


# Convenience function to get logger
def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)

