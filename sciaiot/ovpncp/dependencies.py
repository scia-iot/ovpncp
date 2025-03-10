import logging
import os
from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

app_directory = "/opt/ovpncp"
sqlite_file_name = f"{app_directory}/ovpncp.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_app_directory():
    if not os.path.exists(app_directory):
        os.makedirs(app_directory)
        logger.info(f"Created the app directory: {app_directory}")


def get_session():
    with Session(engine) as session:
        yield session


def create_tables():
    SQLModel.metadata.create_all(engine)
    logger.info("Created all tables.")


def drop_tables():
    SQLModel.metadata.drop_all(engine)
    logger.info("Dropped all tables.")
