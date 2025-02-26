from datetime import datetime
from sciaiot.ovpncp.data.restricted_network import RestrictedNetwork, create, delete, retrieve, retrieve_all, update


def test_create(db_session):
    network = RestrictedNetwork()
    network.start_time = datetime.now()
    network.source_client_id = 1
    network.target_client_id = 2
    
    network = create(network, db_session)
    
    assert network is not None
    assert network.id == 1
    assert network.start_time is not None

def test_read_all(db_session):
    networks = retrieve_all(None, None, db_session)
    
    assert networks is not None
    assert len(networks) == 1
    
    networks = retrieve_all(-1, -1, db_session)
    
    assert len(networks) == 0
    
def test_read_and_update(db_session):
    network = retrieve(1, db_session)
    
    assert network is not None
    assert network.id == 1
    
    network.end_time = datetime.now()
    network = update(network, db_session)
    
    assert network is not None
    assert network.end_time is not None

def test_delete(db_session):
    delete(1, db_session)
