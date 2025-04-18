"""Unit tests for the logging configuration."""

import io
import json
import logging
from unittest.mock import patch

import pytest
import structlog

# Import the function to test
from studyguide.logging_config import configure_logging


@pytestfixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test."""
    # Store original state
    original_manager = logging.manager
    original_root_handlers = logging.root.handlers[:]
    original_root_level = logging.root.level
    original_structlog_config = structlog.get_config()

    yield  # Run the test

    # Restore original state
    logging.manager = original_manager
    logging.root.handlers = original_root_handlers
    logging.root.level = original_root_level
    structlog.configure(**original_structlog_config)
    # Clear contextvars if necessary
    try:
        from structlog.contextvars import clear_contextvars
        clear_contextvars()
    except ImportError:
        pass # Older structlog versions might not have this


@pytest.mark.parametrize(
    "level_str, expected_level",
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
        ("info", logging.INFO), # Case-insensitivity
        ("invalid_level", logging.INFO), # Default fallback
    ],
)
def test_configure_logging_levels(level_str, expected_level):
    """Test that configure_logging sets the correct root logger level."""
    configure_logging(log_level=level_str)
    assert logging.getLogger().level == expected_level


def test_configure_logging_handler_and_formatter():
    """Test that configure_logging adds the correct handler and formatter."""
    configure_logging()
    root_logger = logging.getLogger()

    assert len(root_logger.handlers) == 1
    handler = root_logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, structlog.stdlib.ProcessorFormatter)
    # Check if the formatter uses JSONRenderer
    assert isinstance(
        handler.formatter._processor, structlog.processors.JSONRenderer
    )


@patch("sys.stdout", new_callable=io.StringIO)
def test_logging_output_format(mock_stdout):
    """Test that logs are output in JSON format."""
    configure_logging(log_level="INFO")
    log = structlog.get_logger("test_json_output")
    test_message = "Testing JSON output"
    test_data = {"key": "value", "number": 123}

    log.info(test_message, **test_data)

    # Capture output and parse JSON
    output = mock_stdout.getvalue()
    try:
        log_entry = json.loads(output)
    except json.JSONDecodeError:
        pytest.fail(f"Log output is not valid JSON: {output}")

    # Check content of the JSON log entry
    assert log_entry["event"] == test_message
    assert log_entry["key"] == test_data["key"]
    assert log_entry["number"] == test_data["number"]
    assert log_entry["log_level"] == "info"
    assert log_entry["logger"] == "test_json_output"
    assert "timestamp" in log_entry


@patch("sys.stdout", new_callable=io.StringIO)
def test_logging_exception_info(mock_stdout):
    """Test that exception information is included in logs."""
    configure_logging(log_level="ERROR")
    log = structlog.get_logger("test_exception")

    try:
        raise ValueError("This is a test error")
    except ValueError:
        log.exception("Caught an exception")

    output = mock_stdout.getvalue()
    log_entry = json.loads(output)

    assert log_entry["event"] == "Caught an exception"
    assert log_entry["log_level"] == "error"
    assert "exception" in log_entry
    assert "Traceback" in log_entry["exception"]
    assert "ValueError: This is a test error" in log_entry["exception"]
