import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vault.config.settings import settings
from vault.db.base import Base


@pytest.fixture
def db_engine():
    engine = create_engine(settings.test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def patch_session(db_engine, monkeypatch):
    test_sessionmaker = sessionmaker(bind=db_engine)
    monkeypatch.setattr("vault.db.credentials.Session", test_sessionmaker)
    yield
    with db_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
