from vault.db.models import Credential
from vault.db.session import Session


def save_credential(service_name: str, login: str, encrypted_password: bytes) -> None:
    credential = Credential(
        service_name=service_name,
        login=login,
        encrypted_password=encrypted_password,
    )
    with Session() as session:
        session.add(credential)
        session.commit()
