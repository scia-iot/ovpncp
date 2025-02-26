import ipaddress

import pytest
import sqlalchemy

from sciaiot.ovpncp.data.server import (
    Server,
    VirtualAddress,
    create_server,
    create_virtual_addresses,
    delete_server,
    retrieve_assignable_addresses,
    retrieve_server,
    update_server,
    update_virtual_address,
)


def test_create_server(db_session):
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
    
    network_address, subnet_mask = configs['server'].split()
    network = ipaddress.ip_network(f"{network_address}/{subnet_mask}", strict=False)
    hosts = list(network.hosts())
    
    configs['network_address'] = network_address
    configs['subnet_mask'] = subnet_mask
    configs['ip'] = hosts.pop(0).compressed

    server = Server(**configs)
    server = create_server(server, db_session)
    
    addresses = [VirtualAddress(ip = h.compressed, server=server) for h in hosts]
    create_virtual_addresses(addresses, db_session)

    assert server is not None
    assert server.created_time is not None
    assert server.id == 1
    assert server.network_address == "10.8.0.0"
    assert server.subnet_mask == "255.255.255.0"
    assert server.ip == "10.8.0.1"

def test_read_and_update_server(db_session):
    server = retrieve_server(1, db_session)
    
    assert server is not None
    assert server.id == 1
    assert server.virtual_addresses is not None
    assert len(server.virtual_addresses) == 253
    
    server.persist_key = False
    server.persist_tun = False
    server = update_server(server, db_session)
    
    assert server is not None
    assert server.persist_key is False
    assert server.persist_tun is False
    assert server.updated_time is not None
    
def test_update_virtual_address(db_session):
    server = retrieve_server(1, db_session)
    address = server.virtual_addresses[0]
    
    assert address is not None
    assert address.ip == "10.8.0.2"
    assert address.assignable is True
    
    address.assignable = False
    address = update_virtual_address(address, db_session)
    
    assert address is not None
    assert address.assignable is False
    assert address.updated_time is not None
    
def test_retrieve_assignable_addresses(db_session):
    addresses = retrieve_assignable_addresses(1, db_session)
    
    assert addresses is not None
    assert len(addresses) == 252
    
def test_delete_server(db_session):
    delete_server(1, db_session)
    with pytest.raises(sqlalchemy.exc.NoResultFound) as error:
        retrieve_server(1, db_session)
        
    assert str(error.value) == "No row was found when one was required"
