from datetime import datetime

from sqlalchemy import LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column

from vault.db.base import Base


class VaultConfig(Base):
    __tablename__ = "vault_config"
    id: Mapped[int] = mapped_column(primary_key=True)
    master_password_hash: Mapped[str]
    salt: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Credential(Base):
    __tablename__ = "credentials"
    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str]
    login: Mapped[str]
    encrypted_password: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
