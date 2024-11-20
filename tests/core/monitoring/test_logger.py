import pytest
import json
import logging
from core.monitoring.logger import CoreLogger

@pytest.fixture
def logger():
    return CoreLogger()

def test_json_logging(logger, caplog):
    """Test JSON-formatted logging."""
    with caplog.at_level(logging.INFO):
        logger.logger.info("Test message", extra={"custom": "data"})
    
    # Get last log message
    record = caplog.records[-1]
    log_data = json.loads(record.message)
    
    assert log_data["message"] == "Test message"
    assert log_data["level"] == "INFO"
    assert log_data["custom"] == "data"
    assert "timestamp" in log_data 