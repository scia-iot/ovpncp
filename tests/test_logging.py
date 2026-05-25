import json
import logging
import os
from unittest.mock import patch
from sciaiot.ovpncp.main import setup_logging
from sciaiot.ovpncp.utils.logging import JSONFormatter, mask_sensitive


def test_mask_sensitive_sas():
    sas_url = "https://example.blob.core.windows.net/certs/client.ovpn?sv=2022-11-02&ss=b&srt=o&sp=r&se=2026-04-02T18:31:05Z&st=10:31:05Z&spr=https&sig=SENSITIVE_TOKEN"
    masked = mask_sensitive(sas_url)
    assert "sig=" in masked
    assert "SENSITIVE_TOKEN" not in masked
    assert "sig=***" in masked


def test_mask_sensitive_ip():
    message = "Connection from 1.2.3.4 failed"
    masked = mask_sensitive(message)
    assert "1.2.3.4" not in masked
    assert "1.2.3.4" in message
    assert "***.***.***.***" in masked


def test_json_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test message",
        args=None,
        exc_info=None,
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
