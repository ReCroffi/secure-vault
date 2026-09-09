"""Classe base do SQLAlchemy: todo model (VaultConfig, Credential) herda
dela pra entrar no metadata usado pelas migrations do Alembic."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass