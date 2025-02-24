from datetime import datetime
from typing import List

from sqlmodel import Field, Session, SQLModel, select


class ClientConnection(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    remote_address: str
    connected_time: datetime = None
    disconnected_time: datetime | None = None
    
    client_id: int | None = Field(default=None, foreign_key="client.id")

def create(connection_to_create: ClientConnection, session: Session) -> ClientConnection:
    session.add(connection_to_create)
    session.commit()
    session.refresh(connection_to_create)
    
    return connection_to_create

def read(connection_id: int, session: Session) -> ClientConnection:
    connection = session.exec(select(ClientConnection).filter(ClientConnection.id == connection_id)).first()
    return connection

def read_all(session: Session) -> List[ClientConnection]:
    connections = session.exec(select(ClientConnection)).all()
    return connections

def update(connection_id: int, connection: ClientConnection, session: Session) -> ClientConnection:
    connection_to_update = read(connection_id, session)
    connection_data = connection.model_dump(exclude_unset=True)
        
    for key, value in connection_data.items():
        setattr(connection_to_update, key, value)
    
    session.add(connection_to_update)
    session.commit()
    session.refresh(connection_to_update)
    
    return connection_to_update

def delete(connection_id: int, session: Session):
    connection = read(connection_id, session)
    session.delete(connection)
    session.commit()
