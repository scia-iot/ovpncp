from datetime import datetime
from typing import List

from sqlmodel import Field, Session, SQLModel, select


class RestrictedNetwork(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True) 
    live: bool
    start_time: datetime = None
    end_time: datetime | None = None
    
    source_client_id: int | None = Field(default=None, foreign_key="client.id")
    target_client_id: int | None = Field(default=None, foreign_key="client.id")

def create(network_to_create: RestrictedNetwork, session: Session) -> RestrictedNetwork:
    session.add(network_to_create)
    session.commit()
    session.refresh(network_to_create)
    
    return network_to_create

def read(network_id: int, session: Session) -> RestrictedNetwork:
    network = session.exec(select(RestrictedNetwork).filter(RestrictedNetwork.id == network_id)).first()
    return network

def read_all(session: Session) -> List[RestrictedNetwork]:
    networks = session.exec(select(RestrictedNetwork)).all()
    return networks

def update(network_id: int, network: RestrictedNetwork, session: Session) -> RestrictedNetwork:
    network_to_update = read(network_id, session)
    network_data = network.model_dump(exclude_unset=True)
        
    for key, value in network_data.items():
        setattr(network_to_update, key, value)
    
    session.add(network_to_update)
    session.commit()
    session.refresh(network_to_update)
    
    return network_to_update

def delete(network_id: int, session: Session):
    network = read(network_id, session)
    session.delete(network)
    session.commit()
