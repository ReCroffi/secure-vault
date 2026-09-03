import secrets

from argon2 import PasswordHasher

from vault.db.models import VaultConfig
from vault.db.session import Session


def hash_master_password(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)


def generate_salt() -> bytes:
    return secrets.token_bytes(16)


def create_vault(password: str) -> None:
    vault_config = VaultConfig(
        master_password_hash=hash_master_password(password), salt=generate_salt()
    )
    with Session() as session:
        session.add(vault_config)
        session.commit()
