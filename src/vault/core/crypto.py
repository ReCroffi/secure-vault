"""Cifragem simetrica das senhas dos servicos guardadas no vault.

A `key` usada aqui e a chave de 32 bytes derivada da senha mestra em
`vault.core.master_password.derive_encryption_key` (via Argon2id) - nunca a
senha mestra em si. O Fernet exige a chave em base64 urlsafe, por isso o
re-encode em toda chamada.
"""

import base64

from cryptography.fernet import Fernet, InvalidToken


def encrypt_password(password: str, key: bytes) -> bytes:
    """Cifra a senha de um servico com a chave derivada da senha mestra."""
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key).encrypt(password.encode())


def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
    """Decifra a senha de um servico. Levanta ValueError se a chave nao bater
    ou o dado estiver corrompido (Fernet valida integridade internamente)."""
    fernet_key = base64.urlsafe_b64encode(key)
    try:
        return Fernet(fernet_key).decrypt(encrypted_password).decode()
    except InvalidToken as e:
        raise ValueError("Não foi possível decifrar a senha (credencial corrompida ou chave inválida)") from e
