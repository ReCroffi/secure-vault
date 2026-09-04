import pytest
from sqlalchemy import create_engine

from vault.config.settings import settings


@pytest.fixture
def db_engine():
    engine = create_engine(settings.test_database_url)
    yield engine
    engine.dispose()
