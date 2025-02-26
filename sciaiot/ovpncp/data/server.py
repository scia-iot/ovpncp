from datetime import datetime
from typing import List, Sequence

from sqlmodel import Field, Relationship, Session, SQLModel, select


class Server(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    port: str
    proto: str
    dev: str
    ca: str
    cert: str
    key: str
    dh: str
    data_ciphers_fallback: str
    topology: str
    network_address: str
    subnet_mask: str
    ip: str
    ifconfig_pool_persist: str
    keepalive: str
    persist_key: bool = False
    persist_tun: bool = False
    status: str
    log: str
    verb: str
    explicit_exit_notify: str
    created_time: datetime | None = None
    updated_time: datetime | None = None
    
    virtual_addresses: list["VirtualAddress"] = Relationship(back_populates="server", cascade_delete=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def create_server(server_to_create: Server, session: Session) -> Server:
    server_to_create.created_time = datetime.now()
    
    session.add(server_to_create)
    session.commit()
    session.refresh(server_to_create)
    
    return server_to_create

def retrieve_server(server_id: int, session: Session) -> Server:
    statement = select(Server).where(Server.id == server_id)
    server = session.exec(statement).one()
    return server

def update_server(server: Server, session: Session) -> Server:
    server.updated_time = datetime.now()

    session.add(server)
    session.commit()
    session.refresh(server)

    return server

def delete_server(server_id: int, session: Session):
    server = retrieve_server(server_id, session)
    session.delete(server)
    session.commit()
    

class VirtualAddress(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ip: str
    assignable: bool = True
    created_time: datetime | None = None
    updated_time: datetime | None = None

    server_id: int | None = Field(default=None, foreign_key="server.id")
    server: Server | None = Relationship(back_populates="virtual_addresses")

def create_virtual_addresses(addresses: List[VirtualAddress], session: Session):
    for address in addresses:
        address.created_time = datetime.now()
        session.add(address)
    session.commit()

def retrieve_assignable_addresses(server_id: int, session: Session) -> Sequence[VirtualAddress]:
    statement = select(VirtualAddress).where(VirtualAddress.server_id == server_id, VirtualAddress.assignable)
    addresses = session.exec(statement).all()
    return addresses

def update_virtual_address(address: VirtualAddress, session: Session) -> VirtualAddress:
    address.updated_time = datetime.now()
    
    session.add(address)
    session.commit()
    session.refresh(address)

    return address
