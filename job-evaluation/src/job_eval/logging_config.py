"""Logging configuration with JSON formatting for structured logs."""
import logging
import sys
import json
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["stack_trace"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging with JSON formatter.

    Args:
        level: Logging level (default: INFO)
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True  # Override any existing configuration
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with JSON formatting.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_with_extra(logger: logging.Logger, level: int, message: str, **extra_fields: Any) -> None:
    """
    Log message with extra fields for JSON output.

    Args:
        logger: Logger instance
        level: Logging level
        message: Log message
        **extra_fields: Extra fields to include in JSON
    """
    # Create a LogRecord with extra fields
    record = logger.makeRecord(
        logger.name,
        level,
        "(unknown file)",
        0,
        message,
        (),
        None
    )
    record.extra_fields = extra_fields
    logger.handle(record)


# Initialize logging on module import
setup_logging()
