from sqlalchemy import select

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


def get_credentials_by_service(service_name: str) -> list[Credential]:
    with Session() as session:
        query = select(Credential).where(Credential.service_name == service_name)
        return list(session.execute(query).scalars().all())
