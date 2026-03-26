import json
import logging
import os
from io import StringIO
from unittest.mock import patch
import pytest
from sciaiot.ovpncp.main import setup_logging
from sciaiot.ovpncp.utils.logging import JSONFormatter

def test_json_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=None,
        exc_info=None
    )
    output = formatter.format(record)
    json_output = json.loads(output)
    
    assert json_output["message"] == "Test message"
    assert json_output["levelname"] == "INFO"
    assert json_output["name"] == "test_logger"
    assert "timestamp" in json_output

@patch.dict(os.environ, {"LOG_FORMAT": "json"})
def test_setup_logging_json():
    with patch("logging.config.dictConfig") as mock_dict_config:
        setup_logging()
        args, _ = mock_dict_config.call_args
        config = args[0]
        assert config["handlers"]["console"]["formatter"] == "json"
        assert config["handlers"]["file"]["formatter"] == "json"

@patch.dict(os.environ, {"LOG_FORMAT": "standard"})
def test_setup_logging_standard():
    with patch("logging.config.dictConfig") as mock_dict_config:
        setup_logging()
        args, _ = mock_dict_config.call_args
        config = args[0]
        assert config["handlers"]["console"]["formatter"] == "standard"
        assert config["handlers"]["file"]["formatter"] == "standard"
