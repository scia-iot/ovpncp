from datetime import datetime
from typing import Sequence

from sqlmodel import Field, Session, SQLModel, select


class RestrictedNetwork(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    start_time: datetime | None = None
    end_time: datetime | None = None
    source_client_id: int | None = Field(default=None, foreign_key="client.id")
    target_client_id: int | None = Field(default=None, foreign_key="client.id")

def create(network_to_create: RestrictedNetwork, session: Session) -> RestrictedNetwork:    
    session.add(network_to_create)
    session.commit()
    session.refresh(network_to_create)
    
    return network_to_create

def retrieve(network_id: int, session: Session) -> RestrictedNetwork:
    statement = select(RestrictedNetwork).where(RestrictedNetwork.id == network_id)
    network = session.exec(statement).one()
    return network

def retrieve_all(source_client_id: int | None, target_client_id: int | None, session: Session) -> Sequence[RestrictedNetwork]:
    statement = select(RestrictedNetwork)
    if source_client_id is not None:
        statement = statement.where(RestrictedNetwork.source_client_id == source_client_id)
    if target_client_id is not None:
        statement = statement.where(RestrictedNetwork.target_client_id == target_client_id)
    
    networks = session.exec(statement).all()
    return networks

def update(network_to_update: RestrictedNetwork, session: Session) -> RestrictedNetwork:   
    session.add(network_to_update)
    session.commit()
    session.refresh(network_to_update)
    
    return network_to_update

def delete(network_id: int, session: Session):
    network = retrieve(network_id, session)
    session.delete(network)
    session.commit()
