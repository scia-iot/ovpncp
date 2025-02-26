from datetime import datetime

from sciaiot.ovpncp.data.client import (
    Client,
    Connection,
    create_client,
    create_connection,
    delete_client,
    delete_connection,
    retrieve_client,
    retrieve_clients,
    retrieve_connection,
    retrieve_connections,
    update_client,
    update_connection,
)


def test_create_client(db_session):
    client = Client(name="client_1")
    client.virtual_address_id = 1    
    client = create_client(client, db_session)
    
    assert client is not None
    assert client.id == 1
    assert client.virtual_address_id == 1

def test_retrieve_clients(db_session):
    clients = retrieve_clients(db_session)
    
    assert clients is not None
    assert len(clients) == 1

def test_create_connection(db_session):
    connection = Connection(remote_address="172.205.176.207:60374", connected_time=datetime.now())
    connection.client_id = 1
    
    connection = create_connection(connection, db_session)
    
    assert connection is not None
    assert connection.id == 1

def test_retrieve_connections(db_session):
    connections = retrieve_connections(db_session)
    
    assert connections is not None
    assert len(connections) == 1
    
def test_retrieve_and_update_connection(db_session):
    connection = retrieve_connection(1, db_session)
    
    assert connection is not None
    assert connection.remote_address == "172.205.176.207:60374"
    
    connection.disconnected_time = datetime.now()
    connection = update_connection(connection, db_session)
    
    assert connection is not None
    assert connection.disconnected_time is not None
    
def test_retrieve_and_update_client(db_session):
    client = retrieve_client(1, db_session)
    connections = client.connections
    
    assert client is not None
    assert client.id == 1
    assert len(connections) == 1
    
    client = update_client(client, db_session)
    
    assert client is not None
    assert client.updated_time is not None

def test_delete_connection(db_session):
    delete_connection(1, db_session)

def test_delete_client(db_session):
    delete_client(1, db_session)
