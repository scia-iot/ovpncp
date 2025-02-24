import datetime

from sciaiot.ovpncp.data.client_connection import ClientConnection, create, delete, read, read_all, update


def test_create(db_session):
    connection = ClientConnection()
    connection.remote_address = "172.205.176.207:60374"
    connection.connected_time = datetime.datetime.now()
    connection.client_id = 1
    
    connection = create(connection, db_session)
    
    assert connection is not None
    assert connection.id == 1

def test_read_all(db_session):
    connections = read_all(db_session)
    
    assert connections is not None
    assert len(connections) == 1
    
def test_read_and_update(db_session):
    connection = read(1, db_session)
    
    assert connection is not None
    assert connection.id == 1
    
    connection.disconnected_time = datetime.datetime.now()
    connection = update(1, connection, db_session)
    
    assert connection is not None
    assert connection.disconnected_time is not None

def test_delete(db_session):
    delete(1, db_session)
