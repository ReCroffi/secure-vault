import base64

from cryptography.fernet import Fernet


def encrypt_password(password: str, key: bytes) -> bytes:
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key).encrypt(password.encode())


def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key).decrypt(encrypted_password).decode()
