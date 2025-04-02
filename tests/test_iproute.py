from unittest.mock import MagicMock, patch

from sciaiot.ovpncp.utils import iproute

mocked_routes = """10.8.0.0/24 proto kernel scope link src 10.8.0.1
192.168.1.0/24 via 10.8.0.1
"""


@patch('subprocess.run', return_value=MagicMock(stdout=mocked_routes))
def test_list_routes(mock_run):
    shell_command = ['ip', 'route', 'show', 'dev', 'tun0']
    routes = iproute.list("tun0")
    assert len(routes) == 2
    
    mock_run.assert_called_once_with(
        shell_command, capture_output=True, text=True, check=True)


@patch('subprocess.run')
def test_add_route(mock_run):
    shell_command = 'ip route add 192.168.1.0/24 via 10.8.0.1 dev tun0'
    iproute.add('192.168.1.0/24', '10.8.0.1', "tun0")
    
    mock_run.assert_called_once_with(
        shell_command, shell=True, check=True)


@patch('subprocess.run')
def test_delete_route(mock_run):
    shell_command = 'ip route del 192.168.1.0/24 via 10.8.0.1 dev tun0'
    iproute.delete('192.168.1.0/24 via 10.8.0.1', 'tun0')
    
    mock_run.assert_called_once_with(
        shell_command, shell=True, check=True)
