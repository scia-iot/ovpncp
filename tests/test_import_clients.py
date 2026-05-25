from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.main import app
from sciaiot.ovpncp.utils.openvpn import list_client_certs


@pytest.fixture(name="client")
def client_fixture(db_session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@patch("os.listdir")
def test_list_client_certs_success(mock_listdir):
    # Mocking the directory content
    mock_listdir.return_value = [
        "client1.crt",
        "client2.crt",
        "server.crt",
        "random.txt",
    ]

    clients = list_client_certs()

    assert "client1" in clients
    assert "client2" in clients
    assert "server" not in clients
    assert "random" not in clients


@patch("os.listdir", side_effect=FileNotFoundError)
def test_list_client_certs_not_found(mock_listdir):
    clients = list_client_certs()
    assert clients == []


@patch("sciaiot.ovpncp.utils.openvpn.list_client_certs")
@patch("sciaiot.ovpncp.utils.openvpn.read_client_cert")
def test_import_clients_api(mock_read_cert, mock_list_certs, client: TestClient):
    # 1. First import: two new clients
    mock_list_certs.return_value = ["new_client_1", "new_client_2"]
    mock_read_cert.side_effect = [
        {
            "issued_by": "CA",
            "issued_to": "new_client_1",
            "issued_on": datetime.now(),
            "expires_on": datetime.now(),
        },
        {
            "issued_by": "CA",
            "issued_to": "new_client_2",
            "issued_on": datetime.now(),
            "expires_on": datetime.now(),
        },
    ]

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 2, "updated": 0}

    # 2. Second import: one new, one existing
    mock_list_certs.return_value = ["new_client_1", "new_client_3"]
    mock_read_cert.side_effect = [
        {
            "issued_by": "CA",
            "issued_to": "new_client_1",
            "issued_on": datetime.now(),
            "expires_on": datetime.now(),
        },
        {
            "issued_by": "CA",
            "issued_to": "new_client_3",
            "issued_on": datetime.now(),
            "expires_on": datetime.now(),
        },
    ]

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 1, "updated": 1}

    # 3. Third import: one cert read failure
    mock_list_certs.return_value = ["fail_client"]
    mock_read_cert.side_effect = [{}]

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 0, "updated": 0}
