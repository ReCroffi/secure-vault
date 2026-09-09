"""Engine unico do SQLAlchemy, criado a partir da DATABASE_URL do .env
(ver `vault.config.settings`). Importado por `vault.db.session` pra montar
o sessionmaker - o resto do codigo nunca usa `engine` diretamente."""

from sqlalchemy import create_engine

from vault.config.settings import settings

engine = create_engine(settings.database_url)
