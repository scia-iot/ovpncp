from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
from fastapi.testclient import TestClient

from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.main import app
from tests import test_openvpn


@pytest.fixture(name="client")
def client_fixture(db_session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@patch("builtins.open", new_callable=mock_open, read_data=test_openvpn.server_config_lines)
def test_init_server(mock_run, client: TestClient):
    response = client.get("/server")
    assert response.status_code == 404
    assert response.json() == {"detail": "Server not found"}

    response = client.post("/server")
    assert response.status_code == 200

    server = response.json()
    assert server is not None
    assert server["ip"] == "10.8.0.1"
    assert server["virtual_addresses"] is not None
    assert len(server["virtual_addresses"]) == 253

    mock_run.assert_called_with("/etc/openvpn/server.conf", "r")


def test_get_server(client: TestClient):
    response = client.get("/server")
    assert response.status_code == 200

    server = response.json()
    assert server["ip"] == "10.8.0.1"


@patch("subprocess.run", return_value=MagicMock(stdout=test_openvpn.server_status_active))
def test_get_service_health(mock_run, client: TestClient):
    response = client.get("/server/health")
    assert response.status_code == 200

    health = response.json()
    assert health["status"] == "active (running)"
    assert health["period"] == "15s"

    mock_run.assert_called_once_with(
        ["systemctl", "status", "openvpn@server"], capture_output=True, text=True, check=True)


def test_get_assignable_virtual_addresses(client: TestClient):
    response = client.get("/server/assignable-virtual-addresses")
    assert response.status_code == 200

    addresses = response.json()
    assert len(addresses) == 253


@patch("subprocess.run", return_value=MagicMock(returncode=0))
def test_create_client(mock_run, client: TestClient):
    response = client.get("/clients/test_client")
    assert response.status_code == 404
    assert response.json() == {"detail": "Client 'test_client' not found"}

    response = client.post("/clients", json={"name": "test_client_1"})
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == "test_client_1"
    assert content["id"] == 1

    mock_run.assert_called_with([
        "cd", "/etc/openvpn/easy-rsa/",
        "&&",
        "./easyrsa", "--batch", "build-client-full", "test_client_1", "nopass"
    ], capture_output=True, text=True, check=True)

    response = client.post("/clients", json={"name": "test_client_2"})
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == "test_client_2"
    assert content["id"] == 2

    mock_run.assert_called_with([
        "cd", "/etc/openvpn/easy-rsa/",
        "&&",
        "./easyrsa", "--batch", "build-client-full", "test_client_2", "nopass"
    ], capture_output=True, text=True, check=True)


def test_get_clients(client: TestClient):
    response = client.get("/clients")
    assert response.status_code == 200

    content = response.json()
    assert content is not None
    assert len(content) == 2


@patch("builtins.open", new_callable=mock_open)
def test_assign_virtual_address(mock_run, client: TestClient):
    response = client.put("/clients/test_client_1", json={"ip": "10.0.0.1"})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Virtual address with IP '10.0.0.1' not found"}

    response = client.put("/clients/test_client_1", json={"ip": "10.8.0.2"})
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == "test_client_1"
    assert content["virtual_address"]["ip"] == "10.8.0.2"

    response = client.put("/clients/test_client_2", json={"ip": "10.8.0.3"})
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == "test_client_2"
    assert content["virtual_address"]["ip"] == "10.8.0.3"

    response = client.get("/server/assignable-virtual-addresses")
    addresses = response.json()
    assert len(addresses) == 251

    mock_run.assert_called_with("/var/log/openvpn/ipp.txt", "a")


def test_start_connection(client: TestClient):
    response = client.post(
        "/clients/test_client_1/connections",
        json={"remote_address": "172.205.176.207:60374",
              "connected_time": datetime.now().isoformat()}
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] is not None
    assert content["connected_time"] is not None

    response = client.post(
        "/clients/test_client_2/connections",
        json={"remote_address": "172.205.176.208:60374",
              "connected_time": datetime.now().isoformat()}
    )
    assert response.status_code == 200


@patch('subprocess.run')
def test_create_restricted_network(mock_run, client: TestClient):
    response = client.get("/networks/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Network with ID 1 not found"}

    response = client.post(
        "/networks",
        json={"source_client_name": "test_client_1",
              "destination_client_name": "test_client_2"}
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] == 1
    assert content["source_virtual_address"] == "10.8.0.2"
    assert content["destination_virtual_address"] == "10.8.0.3"
    assert content["start_time"] is not None


def test_close_connection(client: TestClient):
    response = client.put(
        "/clients/test_client_1/connections",
        json={"remote_address": "10.8.0.2",
              "disconnected_time": datetime.now().isoformat()}
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Connection with client 'test_client_1' from '10.8.0.2' not found"}

    response = client.put(
        "/clients/test_client_1/connections",
        json={"remote_address": "172.205.176.207:60374",
              "disconnected_time": datetime.now().isoformat()}
    )
    assert response.status_code == 200

    content = response.json()
    assert content["disconnected_time"] is not None

    response = client.put(
        "/clients/test_client_2/connections",
        json={"remote_address": "172.205.176.208:60374",
              "disconnected_time": datetime.now().isoformat()}
    )
    assert response.status_code == 200


@patch('subprocess.run')
def test_drop_restricted_network(mock_run, client: TestClient):
    response = client.get("/networks?client_id=1")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    assert content[0]["end_time"] is None

    response = client.delete("/networks/1")
    assert response.status_code == 200

    response = client.get("/networks/1")
    assert response.status_code == 200

    content = response.json()
    assert content["end_time"] is not None


def test_get_client(client: TestClient):
    response = client.get("/clients/test_client_1")
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == "test_client_1"
    assert content["virtual_address"]["ip"] == "10.8.0.2"
    assert len(content["connections"]) == 1
