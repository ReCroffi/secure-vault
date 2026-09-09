"""Tabelas do vault (schema em `migrations/versions/`)."""

from datetime import datetime

from sqlalchemy import LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column

from vault.db.base import Base


class VaultConfig(Base):
    """Linha unica (sempre so uma) com o hash da senha mestra e o salt usado
    pra derivar a chave de cifragem (ver `vault.core.master_password`)."""

    __tablename__ = "vault_config"
    id: Mapped[int] = mapped_column(primary_key=True)
    master_password_hash: Mapped[str]
    salt: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Credential(Base):
    """Uma credencial guardada: nome do servico, login e a senha JA CIFRADA
    (`encrypted_password`) - a senha em texto puro nunca toca o banco.
    `service_name` nao e unico de proposito: o mesmo servico pode ter mais
    de um login guardado."""

    __tablename__ = "credentials"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str]
    login: Mapped[str]
    encrypted_password: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
