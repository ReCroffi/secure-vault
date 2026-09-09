"""Fabrica de sessoes do SQLAlchemy. `vault.db.credentials` e
`vault.core.master_password` usam `with Session() as session: ...` pra abrir
uma sessao curta por operacao, em vez de manter uma sessao global aberta."""

from sqlalchemy.orm import sessionmaker

from vault.db.engine import engine

Session = sessionmaker(bind=engine)
