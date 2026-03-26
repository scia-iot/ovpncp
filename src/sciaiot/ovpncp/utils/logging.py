"""Logging utilities for the OpenVPN Control Panel."""
import json
import logging


class JSONFormatter(logging.Formatter):
    """Formatter for JSON structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record into a JSON string."""
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "levelname": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
