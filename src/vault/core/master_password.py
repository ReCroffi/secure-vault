"""Autenticacao pela senha mestra e derivacao da chave de cifragem.

Duas coisas separadas saem da mesma senha mestra, e por isso existem dois
algoritmos Argon2 diferentes na mesma familia (argon2-cffi):
- `hash_master_password`/`verify_master_password` usam o `PasswordHasher` de
  alto nivel so pra CONFERIR a senha no login (gera e guarda um hash com
  salt embutido, formato `$argon2id$...`).
- `derive_encryption_key` usa `hash_secret_raw` (baixo nivel) pra virar a
  senha mestra numa chave de 32 bytes REPRODUTIVEL, usada pra cifrar/decifrar
  as senhas dos servicos (`vault.core.crypto`). Por isso ela recebe o `salt`
  guardado em `VaultConfig`: sem o mesmo salt, a mesma senha gera uma chave
  diferente e nada decifra.

So existe um `VaultConfig` por vault (linha unica na tabela) - por isso os
`scalar_one()`/`scalar_one_or_none()` sem filtro de id.
"""

import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import Type, hash_secret_raw
from sqlalchemy import select

from vault.db.models import VaultConfig
from vault.db.session import Session


def hash_master_password(password: str) -> str:
    """Gera o hash Argon2id da senha mestra, pra guardar em VaultConfig."""
    ph = PasswordHasher()
    return ph.hash(password)


def generate_salt() -> bytes:
    """Gera um salt aleatorio de 16 bytes pra derivacao da chave de cifragem."""
    return secrets.token_bytes(16)


def verify_master_password(password: str) -> bool:
    """Confere a senha digitada contra o hash guardado no vault."""
    with Session() as session:
        vault_config = session.execute(select(VaultConfig)).scalar_one()
        ph = PasswordHasher()
        try:
            ph.verify(vault_config.master_password_hash, password)
            return True
        except VerifyMismatchError:
            return False


def derive_encryption_key(password: str, salt: bytes) -> bytes:
    """Deriva a chave de cifragem (32 bytes) a partir da senha mestra e do
    salt guardado no vault. Mesma senha + mesmo salt = mesma chave sempre."""
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
    """Confere a senha mestra e devolve a chave de cifragem derivada dela.

    Levanta ValueError se a senha estiver errada.
    """
    if verify_master_password(password):
        with Session() as session:
            vault_config = session.execute(select(VaultConfig)).scalar_one()
            salt = vault_config.salt
            key = derive_encryption_key(password=password, salt=salt)
        return key
    else:
        raise ValueError("Senha mestra incorreta")


def create_vault(password: str) -> None:
    """Cria o VaultConfig (hash da senha mestra + salt novo).

    So pode existir um vault: levanta ValueError se ja houver um criado.
    """
    with Session() as session:
        if session.execute(select(VaultConfig)).scalar_one_or_none() is not None:
            raise ValueError("Vault já existente")

        vault_config = VaultConfig(
            master_password_hash=hash_master_password(password),
            salt=generate_salt(),
        )

        session.add(vault_config)
        session.commit()
