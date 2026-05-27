import importlib.resources
import logging
import logging.config
import os
from contextlib import asynccontextmanager

import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sciaiot.ovpncp.dependencies import (
    create_app_directory,
    create_tables,
    init_scripts,
)
from sciaiot.ovpncp.middlewares.azure_security import azure_security_middleware
from sciaiot.ovpncp.middlewares.azure_storage import azure_storage_middleware
from sciaiot.ovpncp.routes import client, network, server

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = os.environ.get("PORT", "8000")
LOG_CONFIG = importlib.resources.files("sciaiot.ovpncp").joinpath("log.yml")


def setup_logging():
    """Initialize logging based on the environment configuration."""
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    with LOG_CONFIG.open("r") as f:
        config = yaml.safe_load(f)

    # Update handlers to use the requested format if it exists in the config
    if log_format in config.get("formatters", {}):
        for handler in config.get("handlers", {}).values():
            handler["formatter"] = log_format

    logging.config.dictConfig(config)


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_app_directory()
    create_tables()
    init_scripts()
    logger.info("Startup events finished.")

    yield

    # shutdown
    logger.info("Shutdown events finished.")


app = FastAPI(lifespan=lifespan)

app.middleware("http")(azure_security_middleware)
app.middleware("http")(azure_storage_middleware)

app.include_router(server.router, prefix="/server", tags=["server"])
app.include_router(client.router, prefix="/clients", tags=["client"])
app.include_router(network.router, prefix="/networks", tags=["server"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch all unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "type": "/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred on the server.",
            "instance": str(request.url),
        },
    )


def run():
    uvicorn.run(app, host=HOST, port=int(PORT), log_config=str(LOG_CONFIG))
