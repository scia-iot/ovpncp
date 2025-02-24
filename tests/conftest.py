import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture(scope="session")
def db_engine(request):
    sqlite_file_name = ".pytest_cache/ovpncp.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    
    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    SQLModel.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session
