import logging
import json
import io
from app.utilities.logger import JsonFormatter

def test_json_formatter():
    formatter = JsonFormatter()
    log_record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=10,
        msg="Test logging message %s",
        args=("format",),
        exc_info=None
    )
    
    formatted_json_str = formatter.format(log_record)
    log_data = json.loads(formatted_json_str)
    
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test_logger"
    assert log_data["message"] == "Test logging message format"
