from unittest.mock import patch
from sciaiot.ovpncp.utils.openvpn import list_client_certs


@patch("os.listdir")
def test_list_client_certs_success(mock_listdir):
    # Mocking the directory content
    mock_listdir.return_value = [
        "client1.crt",
        "client2.crt",
        "server.crt",
        "random.txt",
    ]

    # We expect server.crt to be ignored if we only want clients,
    # but the spec says "scan the Easy-RSA directory ... to identify existing client certificates".
    # Usually, server.crt is also in 'issued'.
    # Let's assume we want everything that is a .crt file for now,
    # or maybe we should exclude 'server.crt'.

    clients = list_client_certs()

    assert "client1" in clients
    assert "client2" in clients
    assert "server" in clients  # For now, let's see if we should exclude it later
    assert "random" not in clients


@patch("os.listdir", side_effect=FileNotFoundError)
def test_list_client_certs_not_found(mock_listdir):
    clients = list_client_certs()
    assert clients == []
