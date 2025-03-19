from datetime import datetime
import os
import stat
from unittest.mock import MagicMock, mock_open, patch

import pytest
from fastapi.testclient import TestClient

from sciaiot.ovpncp.data.server import Client
from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.main import app
from tests import test_openvpn


@pytest.fixture(name='client')
def client_fixture(db_session):
    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@patch('builtins.open', new_callable=mock_open, read_data=test_openvpn.server_config_lines)
def test_init_server(mock_open, client: TestClient):
    response = client.get('/server')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Server not found'}

    response = client.post('/server')
    assert response.status_code == 200

    server = response.json()
    assert server is not None
    assert server['ip'] == '10.8.0.1'
    assert server['script_security'] == '2'
    assert server['virtual_addresses'] is not None
    assert len(server['virtual_addresses']) == 253

    mock_open.assert_called_with('/etc/openvpn/server.conf', 'r')


def test_get_server(client: TestClient):
    response = client.get('/server')
    assert response.status_code == 200

    server = response.json()
    assert server['ip'] == '10.8.0.1'


@patch('subprocess.run', return_value=MagicMock(stdout=test_openvpn.server_status_active))
def test_get_service_health(mock_run, client: TestClient):
    response = client.get('/server/health')
    assert response.status_code == 200

    health = response.json()
    assert health['status'] == 'active (running)'
    assert health['period'] == '15s'

    mock_run.assert_called_once_with(
        ['systemctl', 'status', 'openvpn@server'], capture_output=True, text=True, check=False)


def test_get_assignable_virtual_addresses(client: TestClient):
    response = client.get('/server/assignable-virtual-addresses')
    assert response.status_code == 200

    addresses = response.json()
    assert len(addresses) == 253


cert_details = {
    'issued_by': 'mock',
    'issued_to': 'client',
    'issued_on': datetime.now(),
    'expires_on': datetime.now(),
}


@patch('sciaiot.ovpncp.utils.openvpn.read_client_cert', return_value=cert_details)
@patch('sciaiot.ovpncp.utils.openvpn.build_client', return_value=True)
def test_create_client(mock_build_client, mock_read_client_cert, client: TestClient):
    response = client.get('/clients/test_client')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Client "test_client" not found'}

    response = client.post('/clients', json={'name': 'test_client_1'})
    assert response.status_code == 200

    content = response.json()
    assert content['name'] == 'test_client_1'
    assert content['id'] == 1

    mock_build_client.assert_called_with('test_client_1')
    mock_read_client_cert.assert_called_with('test_client_1')

    response = client.post('/clients', json={'name': 'test_client_2'})
    assert response.status_code == 200

    content = response.json()
    assert content['name'] == 'test_client_2'
    assert content['id'] == 2

    mock_build_client.assert_called_with('test_client_2')
    mock_read_client_cert.assert_called_with('test_client_2')


def test_get_clients(client: TestClient):
    response = client.get('/clients')
    assert response.status_code == 200

    content = response.json()
    assert content is not None
    assert len(content) == 2


@patch('builtins.open', new_callable=mock_open)
def test_assign_virtual_address(mock_open, client: TestClient):
    response = client.put(
        '/clients/test_client_1/assign-ip', json={'ip': '10.0.0.1'})
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Virtual address with IP "10.0.0.1" not found'}

    response = client.put(
        '/clients/test_client_1/assign-ip', json={'ip': '10.8.0.2'})
    assert response.status_code == 200

    content = response.json()
    assert content['name'] == 'test_client_1'
    assert content['virtual_address']['ip'] == '10.8.0.2'

    response = client.put(
        '/clients/test_client_2/assign-ip', json={'ip': '10.8.0.3'})
    assert response.status_code == 200

    content = response.json()
    assert content['name'] == 'test_client_2'
    assert content['virtual_address']['ip'] == '10.8.0.3'

    response = client.get('/server/assignable-virtual-addresses')
    addresses = response.json()
    assert len(addresses) == 251

    mock_open.assert_called_with('/var/log/openvpn/ipp.txt', 'a')


def test_start_connection(client: TestClient):
    response = client.post(
        '/clients/test_client_1/connections',
        json={'remote_address': '172.205.176.207:60374',
              'connected_time': datetime.now().isoformat()}
    )
    assert response.status_code == 200

    content = response.json()
    assert content['id'] is not None
    assert content['connected_time'] is not None

    response = client.post(
        '/clients/test_client_2/connections',
        json={'remote_address': '172.205.176.208:60374',
              'connected_time': datetime.now().isoformat()}
    )
    assert response.status_code == 200


@patch('subprocess.run')
def test_create_restricted_network(mock_run, client: TestClient):
    response = client.get('/networks/1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Network with ID 1 not found'}

    response = client.post(
        '/networks',
        json={'source_client_name': 'test_client_1',
              'destination_client_name': 'test_client_2'}
    )
    assert response.status_code == 200

    content = response.json()
    assert content['id'] == 1
    assert content['source_virtual_address'] == '10.8.0.2'
    assert content['destination_virtual_address'] == '10.8.0.3'
    assert content['start_time'] is not None

    assert mock_run.call_count == 2


@patch('sciaiot.ovpncp.routes.network.get_client_by_name', return_value=Client(name='N/A'))
def test_create_restricted_network_fail(mock_get_client_by_name, client: TestClient):
    response = client.post(
        '/networks',
        json={'source_client_name': 'N/A',
              'destination_client_name': 'N/A'}
    )
    assert response.status_code == 412

    assert mock_get_client_by_name.call_count == 2


def test_close_connection(client: TestClient):
    response = client.put(
        '/clients/test_client_1/connections',
        json={'remote_address': '10.8.0.2',
              'disconnected_time': datetime.now().isoformat()}
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Connection with client "test_client_1" from "10.8.0.2" not found'}

    response = client.put(
        '/clients/test_client_1/connections',
        json={'remote_address': '172.205.176.207:60374',
              'disconnected_time': datetime.now().isoformat()}
    )
    assert response.status_code == 200

    content = response.json()
    assert content['disconnected_time'] is not None

    response = client.put(
        '/clients/test_client_2/connections',
        json={'remote_address': '172.205.176.208:60374',
              'disconnected_time': datetime.now().isoformat()}
    )
    assert response.status_code == 200


@patch('subprocess.run')
def test_drop_restricted_network(mock_run, client: TestClient):
    response = client.get('/networks?client_id=1')
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    assert content[0]['end_time'] is None

    response = client.delete('/networks/1')
    assert response.status_code == 200

    response = client.get('/networks/1')
    assert response.status_code == 200

    content = response.json()
    assert content['end_time'] is not None

    mock_run.assert_called_once()


@patch('builtins.open', new_callable=mock_open)
def test_unassign_virtual_address(mock_open, client: TestClient):
    response = client.delete('/clients/test_client_2/unassign-ip')
    assert response.status_code == 200

    content = response.json()
    assert content['virtual_address'] is None

    response = client.delete('/clients/test_client_2/unassign-ip')
    assert response.status_code == 412

    response = client.get('/clients/test_client_2')
    assert response.status_code == 200

    content = response.json()
    assert content['virtual_address'] is None

    mock_open.assert_called_with('/var/log/openvpn/ipp.txt', 'w')


def test_get_client(client: TestClient):
    response = client.get('/clients/test_client_1')
    assert response.status_code == 200

    content = response.json()

    assert content['name'] == 'test_client_1'
    assert content['virtual_address']['ip'] == '10.8.0.2'
    assert len(content['connections']) == 1
    assert len(content['cert']) is not None


@patch('sciaiot.ovpncp.utils.openvpn.package_client_cert', return_value='test_client_1.zip')
def test_package_client_cert(mock_package_client_cert, client: TestClient):
    response = client.put('/clients/test_client_1/package-cert')
    assert response.status_code == 201

    content = response.json()
    assert content['file'] == 'test_client_1.zip'

    mock_package_client_cert.assert_called_once_with(
        'test_client_1', '/opt/ovpncp/certs')


@patch('builtins.open', new_callable=mock_open, read_data=b'file content in bytes')
@patch('os.stat')
def test_download_client_cert(mock_stat, mock_open, client: TestClient):
    mode = stat.S_IFREG | 0o644
    mock_stat_result = os.stat_result((mode, 0, 0, 0, 0, 0, 1024, 0, 0, 0))
    mock_stat.return_value = mock_stat_result

    response = client.get('/clients/test_client_1/download-cert')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert response.headers['Content-Length'] == '1024'
    assert response.headers['Content-Disposition'] == 'attachment; filename="test_client_1.zip"'

    mock_stat.assert_called_once_with('/opt/ovpncp/certs/test_client_1.zip')
    mock_open.assert_called_with(
        '/opt/ovpncp/certs/test_client_1.zip', 'rb', -1, None, None, None, True, None)


@patch('sciaiot.ovpncp.utils.openvpn.renew_client_cert', return_value=cert_details)
def test_renew_client(mock_renew_client_cert, client: TestClient):
    response = client.put('/clients/test_client_1/renew-cert')
    assert response.status_code == 200

    content = response.json()

    assert content['issued_by'] == 'mock'
    assert content['issued_on'] is not None
    assert content['expires_on'] is not None

    mock_renew_client_cert.assert_called_once_with('test_client_1')


@patch('sciaiot.ovpncp.utils.openvpn.revoke_client', return_value=True)
@patch('sciaiot.ovpncp.utils.openvpn.generate_crl', return_value=True)
def test_revoke_client(mock_generate_crl, mock_revoke_client, client: TestClient):
    response = client.put('/clients/test_client_1/revoke')
    assert response.status_code == 200

    content = response.json()
    assert content['name'] == 'test_client_1'
    assert content['revoked'] is True

    mock_generate_crl.assert_called_once()
    mock_revoke_client.assert_called_once_with('test_client_1')
