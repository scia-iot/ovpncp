from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from sciaiot.ovpncp.data.server import VirtualAddress


class ClientBase(SQLModel):
    name: str


class Client(ClientBase, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", String, unique=True))
    virtual_address_id: Optional[int] = Field(
        default=None, foreign_key="virtualaddress.id", unique=True)
    virtual_address: Optional["VirtualAddress"] = Relationship(
        back_populates="client")
    connections: list["Connection"] = Relationship(
        back_populates="client", cascade_delete=True)


class ConnectionBase(SQLModel):
    remote_address: str
    connected_time: datetime
    disconnected_time: datetime | None = None


class Connection(ConnectionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    client_id: int = Field(default=None, foreign_key="client.id")
    client: Client = Relationship(back_populates="connections")
