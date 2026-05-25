"""Logging utilities for the OpenVPN Control Panel."""

import json
import logging
import re


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


def mask_sensitive(text: str) -> str:
    """Redact sensitive information like SAS tokens and IP addresses from strings."""
    if not isinstance(text, str):
        return text

    # Mask SAS signature (e.g., sig=SENSITIVE_TOKEN)
    text = re.sub(r"sig=[^&]+", "sig=***", text)

    # Mask IPv4 addresses
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "***.***.***.***", text)

    return text
