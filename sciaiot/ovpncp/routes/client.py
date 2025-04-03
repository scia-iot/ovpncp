import ipaddress
import os
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from sciaiot.ovpncp import dependencies
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
from sciaiot.ovpncp.routes.server import get_server
from sciaiot.ovpncp.utils import openvpn

DBSession = Annotated[Session, Depends(get_session)]
router = APIRouter()


class ClientNetworkRequest(BaseModel):
    ip: str
    route_rules: list[str]


class StartConnectionRequest(BaseModel):
    remote_address: str
    connected_time: datetime


class CloseConnectionRequest(BaseModel):
    remote_address: str
    disconnected_time: datetime


@router.post('')
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


@router.get('')
async def retrieve_clients(session: DBSession):
    clients = session.exec(select(Client)).all()
    return clients


@router.get('/{client_name}', response_model=ClientDetails)
async def retrieve_client(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    return client


@router.put('/{client_name}/package-cert')
async def package_client_cert(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    archive = openvpn.package_client_cert(client.name, dependencies.certs_directory)
    return { 'file': archive }


@router.get('/{client_name}/download-cert')
async def download_client_cert(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    file_name = f'{client.name}.zip'
    file_path = os.path.join(dependencies.certs_directory, file_name)
    return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)


@router.put('/{client_name}/renew-cert', response_model=CertBase)
async def renew_client_cert(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    cert = client.cert

    if cert is not None:
        cert_details = openvpn.renew_client_cert(client.name)
        for key, value in cert_details.items():
            setattr(cert, key, value)

        session.add(cert)
        session.commit()
        session.refresh(cert)

        return cert


@router.put('/{client_name}/revoke', response_model=ClientBase)
async def revoke_client(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    client.revoked = True

    openvpn.revoke_client(client.name)
    openvpn.generate_crl()

    session.add(client)
    session.commit()
    session.refresh(client)

    return client


@router.put('/{client_name}/assign-ip', response_model=ClientWithVirtualAddress)
async def assign_virtual_address(client_name: str, address: VirtualAddressBase, session: DBSession):
    statement = select(VirtualAddress).where(VirtualAddress.ip == address.ip)
    virtual_address = session.exec(statement).one_or_none()
    
    if not virtual_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Virtual address with IP "{address.ip}" not found!')

    server = await get_server(session)
    client = get_client_by_name(client_name, session)
    client.virtual_address = virtual_address
    openvpn.assign_client_ip(client.name, virtual_address.ip, server.subnet_mask)
    
    if client.cidr:
        network = ipaddress.ip_network(client.cidr, strict=False)
        openvpn.add_iroute(client.name, f'{network.network_address} {network.netmask}')

    session.add(client)
    session.commit()
    session.refresh(client)

    return client


@router.delete('/{client_name}/unassign-ip', status_code=status.HTTP_204_NO_CONTENT)
async def unassign_virtual_address(client_name: str, session: DBSession):
    client = get_client_by_name(client_name, session)
    
    if not client.virtual_address:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f'Client "{client_name}" has no virtual address assigned!')

    openvpn.unassign_client_ip(client.name)
    client.virtual_address = None
    
    session.add(client)
    session.commit()
    session.refresh(client)


@router.post('/{client_name}/connections')
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


@router.put('/{client_name}/connections')
async def close_connection(client_name: str, request: CloseConnectionRequest, session: DBSession):
    client = get_client_by_name(client_name, session)
    statement = select(Connection).where(
        Connection.remote_address == request.remote_address,
        Connection.client_id == client.id,
        Connection.disconnected_time == None  # noqa: E711
    ).order_by(Connection.connected_time.desc()) # type: ignore
    connection = session.exec(statement).first()
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Connection with client "{client_name}" from "{request.remote_address}" not found!')

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
            detail=f'Client "{client_name}" not found!')

    return client
