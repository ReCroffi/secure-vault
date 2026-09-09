"""Fixtures compartilhadas: fazem os testes usarem `test_database_url` (banco
separado do de desenvolvimento) em vez do `database_url` normal, sem precisar
mudar uma linha sequer do codigo de `vault.db`/`vault.core`.
"""

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from vault.config.settings import settings
from vault.db.base import Base


@pytest.fixture
def db_engine():
    """Engine apontando pro banco de teste. Descartado (`dispose`) no fim de
    cada teste que o usa."""
    engine = create_engine(settings.test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def patch_session(db_engine, monkeypatch):
    """Roda automaticamente em TODO teste (autouse=True): troca o `Session`
    ja importado dentro de `vault.db.credentials` e
    `vault.core.master_password` por um sessionmaker ligado ao banco de
    teste. So funciona nesses dois modulos porque sao os unicos que abrem
    sessao (`with Session() as session`) - se outro modulo passar a acessar
    o banco direto, precisa ganhar uma linha de monkeypatch aqui tambem.
    Limpa as tabelas antes E depois do teste, pra um teste que falha no meio
    nao sujar o proximo.
    """
    test_sessionmaker = sessionmaker(bind=db_engine)
    monkeypatch.setattr("vault.db.credentials.Session", test_sessionmaker)
    monkeypatch.setattr("vault.core.master_password.Session", test_sessionmaker)
    _limpar_tabelas(db_engine)
    yield
    _limpar_tabelas(db_engine)


def _limpar_tabelas(engine: Engine) -> None:
    """Apaga todas as linhas de todas as tabelas, na ordem inversa do
    metadata (pra respeitar foreign keys, se algum dia existirem)."""
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
