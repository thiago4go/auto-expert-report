"""Logging configuration using structlog."""

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structlog for structured logging.

    Outputs JSON logs to stdout.

    Args:
        log_level: The minimum log level to output (e.g., "DEBUG", "INFO").
    """
    log_level_upper = log_level.upper()
    numeric_log_level = getattr(logging, log_level_upper, logging.INFO)

    # Define shared processors for structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors
        + [
            # Prepare event dict for standard library logging
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the underlying standard library logging handler
    formatter = structlog.stdlib.ProcessorFormatter(
        # Render event dict as JSON
        processor=structlog.processors.JSONRenderer(),
        # Add foreign processors if needed (e.g., from other libraries)
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    # Remove existing handlers if any to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_log_level)

    # Suppress overly verbose logs from libraries if needed
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("aiocache").setLevel(logging.WARNING)

    # Example usage after configuration:
    # log = structlog.get_logger("my_module")
    # log.info("Logging configured", level=log_level_upper)


# Automatically configure logging on import?
# Generally better to call explicitly from main entry point (e.g., CLI)
# configure_logging()

if __name__ == "__main__":
    # Example of configuring and using the logger
    configure_logging(log_level="DEBUG")
    log = structlog.get_logger("config_test")
    log.debug("This is a debug message", data={"key": "value"})
    log.info("This is an info message")
    log.warning("This is a warning")
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("An error occurred")
