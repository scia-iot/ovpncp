import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import logging

# We will test the exception handler on a fresh app first to TDD the handler logic
test_app = FastAPI()

@test_app.get("/test-exception")
async def trigger_exception():
    raise RuntimeError("Test exception")

@pytest.fixture(name="client")
def client_fixture():
    return TestClient(test_app)

def test_global_exception_handler_returns_500(client: TestClient):
    """
    Test that an unhandled exception results in a 500 status code.
    """
    response = client.get("/test-exception")
    assert response.status_code == 500

def test_global_exception_handler_rfc7807_format(client: TestClient):
    """
    Test that the response body follows RFC 7807 Problem Details format.
    """
    # Note: This will fail until the handler is implemented and registered on test_app
    response = client.get("/test-exception")
    data = response.json()
    
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert data["status"] == 500
    assert "detail" in data
    assert "instance" in data

def test_global_exception_handler_no_stack_trace(client: TestClient):
    """
    Test that no stack trace is exposed in the response.
    """
    response = client.get("/test-exception")
    content = response.text
    
    # Check for common stack trace markers
    assert "Traceback" not in content
    assert "RuntimeError: Test exception" not in content

def test_global_exception_handler_logs_error(client: TestClient, caplog):
    """
    Test that the exception is logged.
    """
    with caplog.at_level(logging.ERROR):
        client.get("/test-exception")
    
    assert "Test exception" in caplog.text
    assert "RuntimeError" in caplog.text
