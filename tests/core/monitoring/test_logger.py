import pytest
import logging
import json
from core.monitoring.logger import CoreLogger

@pytest.fixture
def logger():
    """Provide a logger instance."""
    return CoreLogger()

def test_json_logging(logger, caplog):
    """Test JSON-formatted logging."""
    with caplog.at_level(logging.INFO):
        logger.info("Test message", extra={"custom": "data"})
    
    # Get last log record
    record = caplog.records[-1]
    # Get formatted message using logger's formatter
    formatted_message = logger.formatter.format(record)
    log_data = json.loads(formatted_message)
    
    assert log_data["message"] == "Test message"
    assert log_data["data"] == {"custom": "data"}

def test_plain_logging(logger, caplog):
    """Test plain logging without extra data."""
    with caplog.at_level(logging.INFO):
        logger.info("Test message")
    
    # Get last log record
    record = caplog.records[-1]
    # Get formatted message using logger's formatter
    formatted_message = logger.formatter.format(record)
    log_data = json.loads(formatted_message)
    
    assert log_data["message"] == "Test message"
    assert log_data["data"] == {}