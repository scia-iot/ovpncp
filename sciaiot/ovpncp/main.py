import importlib.resources
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from sciaiot.ovpncp.dependencies import (
    create_app_directory,
    create_tables,
    init_scripts,
)
from sciaiot.ovpncp.routes import client, network, server

log_config_path = importlib.resources.files('sciaiot.ovpncp').joinpath('log.yml')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_app_directory()
    create_tables()
    init_scripts()
    logger.info('Startup events finished.')

    yield

    # shutdown
    logger.info('Shutdown events finished.')

app = FastAPI(lifespan=lifespan)
app.include_router(server.router, prefix='/server', tags=['server'])
app.include_router(client.router, prefix='/clients', tags=['client'])
app.include_router(network.router, prefix='/networks', tags=['server'])


def run():
    uvicorn.run(app, host='127.0.0.1', port=8000, log_config=str(log_config_path))
