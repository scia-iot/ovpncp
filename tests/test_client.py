import datetime

from sciaiot.ovpncp.data.client import Client, create, delete, read, read_all, update


def test_create(db_session):
    client = Client()
    client.name = "client_1"
    client.ip = "10.8.0.1"
    client.created_time = datetime.datetime.now()
    client.expired_time = datetime.datetime.now() + datetime.timedelta(days=90)
    
    client = create(client, db_session)
    
    assert client is not None
    assert client.id == 1

def test_read_all(db_session):
    clients = read_all(db_session)
    
    assert clients is not None
    assert len(clients) == 1
    
def test_read_and_update(db_session):
    client = read(1, db_session)
    
    assert client is not None
    assert client.id == 1
    
    client.renewed_time = datetime.datetime.now() + datetime.timedelta(days=90)
    client.expired_time = datetime.datetime.now() + datetime.timedelta(days=180)
    client = update(1, client, db_session)
    
    assert client is not None
    assert client.expired_time is not None

def test_delete(db_session):
    delete(1, db_session)
