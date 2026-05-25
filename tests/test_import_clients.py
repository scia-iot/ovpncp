from datetime import datetime
from unittest.mock import mock_open, patch

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
@patch("sciaiot.ovpncp.utils.openvpn.read_client_ip")
def test_import_clients_api(
    mock_read_ip, mock_read_cert, mock_list_certs, client: TestClient
):
    from tests.test_openvpn import server_config_lines

    # Use a unique IP range for this test to avoid collisions with other tests
    # since we are sharing a session-scoped database.
    unique_config = server_config_lines.replace(
        "server 10.8.0.0 255.255.255.0", "server 10.9.0.0 255.255.255.0"
    )

    # Setup: Create some virtual addresses in DB
    # We need a server first
    with patch("builtins.open", new_callable=mock_open, read_data=unique_config):
        client.post("/server")

    # 1. First import: two new clients, one with IP
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
    mock_read_ip.side_effect = ["10.9.0.2", None]

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 2, "updated": 0}

    # Verify IP assignment
    response = client.get("/clients/new_client_1")
    assert response.json()["virtual_address"]["ip"] == "10.9.0.2"

    response = client.get("/clients/new_client_2")
    assert response.json()["virtual_address"] is None

    # 2. Second import: update existing client with new IP
    mock_list_certs.return_value = ["new_client_2"]
    mock_read_cert.side_effect = [
        {
            "issued_by": "CA",
            "issued_to": "new_client_2",
            "issued_on": datetime.now(),
            "expires_on": datetime.now(),
        }
    ]
    mock_read_ip.side_effect = ["10.9.0.3"]

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 0, "updated": 1}

    response = client.get("/clients/new_client_2")
    assert response.json()["virtual_address"]["ip"] == "10.9.0.3"

    # 3. Third import: one cert read failure
    mock_list_certs.return_value = ["fail_client"]
    mock_read_cert.side_effect = [{}]
    mock_read_ip.return_value = None

    response = client.post("/clients/import")
    assert response.status_code == 200
    assert response.json() == {"added": 0, "updated": 0}
