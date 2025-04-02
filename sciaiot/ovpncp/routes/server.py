import ipaddress
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from sciaiot.ovpncp.data.server import (
    Server,
    ServerWithVirtualAddresses,
    VirtualAddress,
)
from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.utils import iproute, openvpn

DBSession = Annotated[Session, Depends(get_session)]
router = APIRouter()


class RouteRequest(BaseModel):
    network: str


@router.post('', response_model=ServerWithVirtualAddresses)
async def init_server(session: DBSession):
    server = load_from_config()

    session.add(server)
    session.commit()
    session.refresh(server)

    return server


@router.get('')
async def get_server(session: DBSession):
    server = session.exec(select(Server)).one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Server not found!')

    return server


@router.get('/health')
async def get_service_health():
    service_health = openvpn.get_status()
    return service_health


@router.get('/assignable-virtual-addresses')
async def get_assignable_virtual_addresses(session: DBSession):
    statement = select(VirtualAddress).where(VirtualAddress.client == None)  # noqa: E711, is doesn't work here...
    addresses = session.exec(statement).all()
    return addresses


@router.get('/routes')
async def get_routes(session: DBSession):
    server = await get_server(session)
    routes = iproute.list(server.dev)
    return routes


@router.post('/routes', status_code=status.HTTP_204_NO_CONTENT)
async def add_route(request: RouteRequest, session: DBSession):
    if not is_valid_address(request.network):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Only internal network address is allowed!'
        )
    
    server = await get_server(session)
    iproute.add(request.network, server.ip, server.dev)


@router.delete('/routes', status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(network:str, session: DBSession):
    server = await get_server(session)
    routes = iproute.list(server.dev)
    
    target = None
    for route in routes:
        if route.startswith(network):
            target = route
            break
    
    if target:
        iproute.delete(target, server.dev)
    else:    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Network "{network}" not found in routes!'
    )


def load_from_config():
    config = openvpn.get_server_config()

    network_address, subnet_mask = config['server'].split()
    network = ipaddress.ip_network(
        f'{network_address}/{subnet_mask}', strict=False)
    hosts = list(network.hosts())

    config['network_address'] = network_address
    config['subnet_mask'] = subnet_mask
    config['ip'] = hosts.pop(0).compressed
    config['dev'] = f'{config["dev"]}0'

    server = Server(**config)
    server.virtual_addresses = [VirtualAddress(
        ip=h.compressed, server=server) for h in hosts]

    return server


def is_valid_address(network):
    try:
        net = ipaddress.ip_network(network)
        return net.is_private
    except ValueError:
        return False
