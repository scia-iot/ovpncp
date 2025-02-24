from datetime import datetime
from sciaiot.ovpncp.data.server import Server, create, read, update

def test_create(db_session):
    configs = {
        'port': '1194', 
        'proto': 'udp', 
        'dev': 'tun', 
        'ca': 'ca.crt', 
        'cert': 'server.crt', 
        'key': 'server.key', 
        'dh': 'dh2048.pem', 
        'data_ciphers_fallback': 'AES-256-CBC', 
        'topology': 'subnet', 
        'server': '10.8.0.0 255.255.255.0', 
        'ifconfig_pool_persist': '/var/log/openvpn/ipp.txt', 
        'keepalive': '10 120', 
        'persist-key': True, 
        'persist-tun': True, 
        'status': '/var/log/openvpn/openvpn-status.log', 
        'log': '/var/log/openvpn/openvpn.log', 
        'verb': '3', 
        'explicit_exit_notify': '1'
    }
    server = Server(**configs)
    server.created_time = datetime.now()
    server = create(server, db_session)
    
    assert server is not None
    assert server.created_time is not None
    assert server.id == 1
    assert server.ip == "10.8.0.0"
    assert server.subnet_mask == "255.255.255.0"

def test_read_and_update(db_session):
    server = read(1, db_session)
    
    assert server is not None
    assert server.id == 1
    
    server.persist_key = False
    server.persist_tun = False
    server.updated_time = datetime.now()
    server = update(1, server, db_session)
    
    assert server is not None
    assert server.persist_key is False
    assert server.persist_tun is False
    assert server.updated_time is not None