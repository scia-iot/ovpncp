from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from sciaiot.ovpncp.data.network import RestrictedNetwork
from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.routes.client import get_client_by_name
from sciaiot.ovpncp.utils import iptables, openvpn

DBSession = Annotated[Session, Depends(get_session)]
router = APIRouter()


class RestrictedNetworkRequest(BaseModel):
    source_name: str
    destination_name: str
    private_network_addresses: str | None = None


@router.post('')
async def create_restricted_network(request: RestrictedNetworkRequest, session: DBSession):
    source = get_client_by_name(request.source_name, session)
    destination = get_client_by_name(request.destination_name, session)
    
    if not source.virtual_address or not destination.virtual_address:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail='Virtual address must be assigned to both source and destination client!'
        )
    
    network = RestrictedNetwork(
        source_name=source.name,
        source_virtual_address=source.virtual_address.ip,
        destination_name=destination.name,
        destination_virtual_address=destination.virtual_address.ip,
        private_network_addresses=request.private_network_addresses or '',
        start_time=datetime.now(),
    )

    # add those rules before the final one on iptables
    chain = 'FORWARD'
    size = len(iptables.list_rules(chain))
    if network.private_network_addresses:
        all = network.iptable_rules() + (network.private_iptable_rules())
        iptables.apply_rules(chain, size, all)
        openvpn.push_client_routes(source.name, network.push_routes(destination.virtual_address.ip))
    else:
        iptables.apply_rules(chain, size, network.iptable_rules())
        
    session.add(network)
    session.commit()
    session.refresh(network)
    
    return network


@router.get('')
async def retrieve_restricted_networks(source_name: str, session: DBSession):
    statement = select(RestrictedNetwork).where(
        RestrictedNetwork.source_name == source_name)
    networks = session.exec(statement).all()
    return networks


@router.get('/{network_id}')
async def retrieve_restricted_network(network_id: int, session: DBSession):
    statement = select(RestrictedNetwork).where(
        RestrictedNetwork.id == network_id)
    network = session.exec(statement).one_or_none()
    
    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Network with ID {network_id} not found!')
        
    return network


@router.delete('/{network_id}', status_code=status.HTTP_204_NO_CONTENT)
async def drop_restricted_network(network_id: int, session: DBSession):
    network = await retrieve_restricted_network(network_id, session)
    network.end_time = datetime.now()
    
    chain = 'FORWARD'    
    if network.private_network_addresses:
        source = get_client_by_name(network.source_name, session)
        openvpn.pull_client_routes(source.name)
        all = network.iptable_rules() + network.private_iptable_rules()
        iptables.drop_rules(chain, all)
    else:
        iptables.drop_rules(chain, network.iptable_rules())

    session.add(network)
    session.commit()
