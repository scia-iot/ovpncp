from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from sciaiot.ovpncp.data.network import RestrictedNetwork
from sciaiot.ovpncp.dependencies import get_session
from sciaiot.ovpncp.routes.client import get_client_by_name
from sciaiot.ovpncp.utils import iptables


DBSession = Annotated[Session, Depends(get_session)]
router = APIRouter()


class RestrictedNetworkRequest(BaseModel):
    source_client_name: str
    destination_client_name: str


@router.post("")
async def create_restricted_network(request: RestrictedNetworkRequest, session: DBSession):
    source = get_client_by_name(request.source_client_name, session)
    destination = get_client_by_name(request.destination_client_name, session)

    if not source.virtual_address or not destination.virtual_address:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Virtual address must be assigned to both source and destination client!"
        )

    network = RestrictedNetwork(
        client_id=source.id,
        source_virtual_address=source.virtual_address.ip,
        destination_virtual_address=destination.virtual_address.ip,
        start_time=datetime.now(),
    )

    # add those rules before the final one on iptables
    chain = "FORWARD"
    rules = iptables.list_rules(chain)
    iptables.apply_rules(chain, len(rules), network.iptable_rules())

    session.add(network)
    session.commit()
    session.refresh(network)

    return network


@router.get("")
async def retrieve_restricted_networks(client_id: int, session: DBSession):
    statement = select(RestrictedNetwork).where(
        RestrictedNetwork.client_id == client_id)
    networks = session.exec(statement).all()
    return networks


@router.get("/{network_id}")
async def retrieve_restricted_network(network_id: int, session: DBSession):
    statement = select(RestrictedNetwork).where(
        RestrictedNetwork.id == network_id)
    network = session.exec(statement).one_or_none()

    if not network:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network with ID {network_id} not found")

    return network


@router.delete("/{network_id}")
async def drop_restricted_network(network_id: int, session: DBSession):
    network = await retrieve_restricted_network(network_id, session)
    network.end_time = datetime.now()

    chain = "FORWARD"
    iptables.drop_rules(chain, network.iptable_rules())

    session.add(network)
    session.commit()
