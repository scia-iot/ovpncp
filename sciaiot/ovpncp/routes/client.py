from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from sciaiot.ovpncp.data.server import (
    Cert,
    CertBase,
    Client,
    ClientBase,
    ClientDetails,
    ClientWithVirtualAddress,
    Connection,
    VirtualAddress,
    VirtualAddressBase,
)
from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.utils import openvpn

DBSession = Annotated[Session, Depends(get_session)]
router = APIRouter()


class StartConnectionRequest(BaseModel):
    remote_address: str
    connected_time: datetime


class CloseConnectionRequest(BaseModel):
    remote_address: str
    disconnected_time: datetime


@router.post("")
async def create_client(request: ClientBase, session: DBSession):
    client = Client.model_validate(request)
    openvpn.build_client(client.name)
    
    cert_details = openvpn.read_client_cert(client.name)
    cert = Cert(**cert_details)
    cert.client = client
    
    session.add(client)
    session.add(cert)
    session.commit()
    session.refresh(client)
    
    return client


@router.get("")
async def retrieve_clients(session: DBSession):
    clients = session.exec(select(Client)).all()
    return clients


@router.get("/{client_name}", response_model=ClientDetails)
async def retrieve_client(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    return client


@router.put("/{client_name}/renew-cert", response_model=CertBase)
async def renew_client_cert(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    cert_details = openvpn.renew_client_cert(client.name)
    cert = Cert(**cert_details)
    cert.client = client
    
    session.add(cert)
    session.commit()
    session.refresh(cert)
    
    return cert


@router.put("/{client_name}/revoke", response_model=ClientBase)
async def revoke_client(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    client.revoked = True
    
    openvpn.revoke_client(client.name)
    openvpn.generate_crl()
    
    session.add(client)
    session.commit()
    session.refresh(client)
    
    return client


@router.put("/{client_name}", response_model=ClientWithVirtualAddress)
async def assign_virtual_address(client_name: str, address: VirtualAddressBase, session: DBSession):
    statement = select(VirtualAddress).where(VirtualAddress.ip == address.ip)
    virtual_address = session.exec(statement).one_or_none()
    if not virtual_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Virtual address with IP '{address.ip}' not found")

    client = get_client_by_name(client_name, session)
    client.virtual_address = virtual_address
    openvpn.assign_client_ip(client.name, virtual_address.ip)

    session.add(client)
    session.commit()
    session.refresh(client)

    return client


@router.post("/{client_name}/connections")
async def start_connection(client_name: str, request: StartConnectionRequest, session: DBSession):
    client = get_client_by_name(client_name, session)
    connection = Connection(
        client=client,
        remote_address=request.remote_address,
        connected_time=request.connected_time,
    )

    session.add(connection)
    session.commit()
    session.refresh(connection)

    return connection


@router.put("/{client_name}/connections")
async def close_connection(client_name: str, request: CloseConnectionRequest, session: DBSession):
    client = get_client_by_name(client_name, session)
    statement = select(Connection).where(
        Connection.remote_address == request.remote_address,
        Connection.client_id == client.id
    )
    connection = session.exec(statement).one_or_none()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with client '{client_name}' from '{request.remote_address}' not found")

    connection.disconnected_time = request.disconnected_time

    session.add(connection)
    session.commit()
    session.refresh(connection)

    return connection


def get_client_by_name(client_name: str, session: Session) -> Client:
    statement = select(Client).where(Client.name == client_name)
    client = session.exec(statement).one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client '{client_name}' not found")

    return client
