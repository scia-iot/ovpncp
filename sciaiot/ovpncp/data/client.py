from datetime import datetime
from typing import List

from sqlmodel import Field, Session, SQLModel, select


class Client(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True) 
    name: str
    ip: str
    created_time: datetime = None
    expired_time: datetime = None
    renewed_time: datetime | None = None

def create(client_to_create: Client, session: Session) -> Client:
    session.add(client_to_create)
    session.commit()
    session.refresh(client_to_create)
    
    return client_to_create

def read(client_id: int, session: Session) -> Client:
    client = session.exec(select(Client).filter(Client.id == client_id)).first()
    return client

def read_all(session: Session) -> List[Client]:
    clients = session.exec(select(Client)).all()
    return clients

def update(client_id: int, client: Client, session: Session) -> Client:
    client_to_update = read(client_id, session)
    client_data = client.model_dump(exclude_unset=True)
        
    for key, value in client_data.items():
        setattr(client_to_update, key, value)
    
    session.add(client_to_update)
    session.commit()
    session.refresh(client_to_update)
    
    return client_to_update

def delete(client_id: int, session: Session):
    client = read(client_id, session)
    session.delete(client)
    session.commit()
