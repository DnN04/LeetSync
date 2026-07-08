import json
import logging
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Custom logging Formatter that outputs logs in structured JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # Include exception traceback if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Include extra attributes passed to log call
        extra_keys = set(record.__dict__.keys()) - {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process'
        }
        for key in extra_keys:
            log_data[key] = record.__dict__[key]
            
        return json.dumps(log_data)

def setup_logging(level: str = "INFO") -> None:
    """Configures root logger to use JsonFormatter outputting to stdout."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
