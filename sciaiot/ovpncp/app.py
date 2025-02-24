import logging
from contextlib import asynccontextmanager
from sciaiot.ovpncp.database import create_db_and_tables

from fastapi import FastAPI

from sciaiot.ovpncp.server import client, connection, status

logger = logging.getLogger(__name__)

@asynccontextmanager
def lifespan(app: FastAPI):
    # startup
    create_db_and_tables()
    logger.info("Startup events finished.")
    
    yield

    # shutdown
    logger.info("Shutdown events finished.")
    
app = FastAPI(lifespan=lifespan)

app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(client.router, prefix="/clients", tags=["client"])
app.include_router(connection.router, prefix="/connections", tags=["connection"])
