from sqlalchemy import create_engine
from vault.config.settings import settings

engine = create_engine(settings.database_url)