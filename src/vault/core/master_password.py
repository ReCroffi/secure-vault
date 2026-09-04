import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import Type, hash_secret_raw
from sqlalchemy import select

from vault.db.models import VaultConfig
from vault.db.session import Session


def hash_master_password(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)


def generate_salt() -> bytes:
    return secrets.token_bytes(16)


def verify_master_password(password: str) -> bool:
    with Session() as session:
        vault_config = session.execute(select(VaultConfig)).scalar_one()
        ph = PasswordHasher()
        try:
            ph.verify(vault_config.master_password_hash, password)
            return True
        except VerifyMismatchError:
            return False


def derive_encryption_key(password: str, salt: bytes) -> bytes:
    hash_raw = hash_secret_raw(
        password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )
    return hash_raw


def login(password: str) -> bytes:
    if verify_master_password(password):
        with Session() as session:
            vault_config = session.execute(select(VaultConfig)).scalar_one()
            salt = vault_config.salt
            key = derive_encryption_key(password=password, salt=salt)
        return key
    else:
        raise ValueError("Senha mestra incorreta")


def vault_exists() -> bool:
    with Session() as session:
        return session.execute(select(VaultConfig)).scalar_one_or_none() is not None


def create_vault(password: str) -> None:
    if vault_exists():
        raise ValueError("Vault já existente")
    else:
        vault_config = VaultConfig(
            master_password_hash=hash_master_password(password), salt=generate_salt()
        )
        with Session() as session:
            session.add(vault_config)
            session.commit()
