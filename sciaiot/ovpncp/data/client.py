from datetime import datetime
from typing import Sequence

from sqlmodel import Field, Relationship, Session, SQLModel, select


class Client(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True) 
    name: str
    created_time: datetime | None = None
    expired_time: datetime | None = None
    updated_time: datetime | None = None
    
    virtual_address_id: int | None = Field(default=None, foreign_key="virtualaddress.id")
    connections: list["Connection"] = Relationship(back_populates="client", cascade_delete=True)

def create_client(client_to_create: Client, session: Session) -> Client:
    client_to_create.created_time = datetime.now()
    
    session.add(client_to_create)
    session.commit()
    session.refresh(client_to_create)
    
    return client_to_create

def retrieve_client(client_id: int, session: Session) -> Client:
    statement = select(Client).where(Client.id == client_id)
    client = session.exec(statement).one()
    return client

def retrieve_clients(session: Session) -> Sequence[Client]:
    clients = session.exec(select(Client)).all()
    return clients

def update_client(client: Client, session: Session) -> Client:
    client.updated_time = datetime.now()
    
    session.add(client)
    session.commit()
    session.refresh(client)
    
    return client

def delete_client(client_id: int, session: Session):
    client = retrieve_client(client_id, session)
    session.delete(client)
    session.commit()


class Connection(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    remote_address: str
    connected_time: datetime
    disconnected_time: datetime | None = None
    
    client_id: int | None = Field(default=None, foreign_key="client.id")
    client: Client| None = Relationship(back_populates="connections")

def create_connection(connection: Connection, session: Session) -> Connection:
    session.add(connection)
    session.commit()
    session.refresh(connection)
    
    return connection

def retrieve_connection(connection_id: int, session: Session) -> Connection:
    statement = select(Connection).where(Connection.id == connection_id)
    connection = session.exec(statement).one()
    return connection

def retrieve_connections(session: Session) -> Sequence[Connection]:
    connections = session.exec(select(Connection)).all()
    return connections

def update_connection(connection: Connection, session: Session) -> Connection:   
    session.add(connection)
    session.commit()
    session.refresh(connection)
    
    return connection

def delete_connection(connection_id: int, session: Session):
    connection = retrieve_connection(connection_id, session)
    session.delete(connection)
    session.commit()
