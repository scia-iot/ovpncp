from datetime import datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, select


class Server(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    port: str
    proto: str
    dev: str
    ca: str
    cert: str
    key: str
    dh: str
    data_ciphers_fallback: str
    topology: str
    ip: str
    subnet_mask: str
    ifconfig_pool_persist: str
    keepalive: str
    persist_key: bool = False
    persist_tun: bool = False
    status: str
    log: str
    verb: str
    explicit_exit_notify: str
    
    created_time: datetime = None
    updated_time: datetime | None = None

    def __init__(self, **kwargs):
        server_str = kwargs.pop('server', None)
        if server_str:
            server_ip, subnet_mask = server_str.split()
            kwargs['ip'] = server_ip
            kwargs['subnet_mask'] = subnet_mask
        super().__init__(**kwargs)


def create(server_to_create: Server, session: Session) -> Server:
    session.add(server_to_create)
    session.commit()
    session.refresh(server_to_create)
    return server_to_create


def read(server_id: int, session: Session) -> Server:
    server = session.exec(select(Server).filter(Server.id == server_id)).first()
    return server


def update(server_id: int, server: Server, session: Session) -> Server:
    server_to_update = read(server_id, session)
    server_data = server.model_dump(exclude_unset=True)

    for key, value in server_data.items():
        setattr(server_to_update, key, value)

    session.add(server_to_update)
    session.commit()
    session.refresh(server_to_update)

    return server_to_update
