import importlib.resources
import logging
import os
from pathlib import Path
import shutil

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

app_directory = '/opt/ovpncp'
certs_directory = f'{app_directory}/certs'
scripts_directory = f'{app_directory}/scripts'
sqlite_file_name = f'{app_directory}/ovpncp.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'
connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

def create_app_directory():
    if not os.path.exists(app_directory):
        os.makedirs(app_directory)
        os.makedirs(certs_directory)
        os.makedirs(scripts_directory)
        logger.info('Created the app directory & subdirectories.')


def copy_scripts():
    target_folder = Path(scripts_directory)
    with importlib.resources.path('sciaiot.ovpncp', 'scripts') as source_path:
        if target_folder.exists():
            shutil.rmtree(target_folder)
            
        shutil.copytree(source_path, target_folder)
        logger.info('Copied scripts to the app directory.')


def get_session():
    with Session(engine) as session:
        yield session


def create_tables():
    SQLModel.metadata.create_all(engine)
    logger.info('Created all tables.')


def drop_tables():
    SQLModel.metadata.drop_all(engine)
    logger.info('Dropped all tables.')
