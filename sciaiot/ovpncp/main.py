import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from sciaiot.ovpncp.dependencies import create_tables
from sciaiot.ovpncp.routes import client, network, server

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_tables()
    logger.info("Startup events finished.")

    yield

    # shutdown
    logger.info("Shutdown events finished.")

app = FastAPI(lifespan=lifespan)
app.include_router(server.router, prefix="/server", tags=["server"])
app.include_router(client.router, prefix="/clients", tags=["client"])
app.include_router(network.router, prefix="/networks", tags=["server"])


def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)
