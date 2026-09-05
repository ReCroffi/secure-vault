from sqlalchemy import select

from vault.db.models import Credential
from vault.db.session import Session


def save_credential(service_name: str, login: str, encrypted_password: bytes) -> None:
    """Insere uma credencial nova. A senha ja deve chegar cifrada."""
    credential = Credential(
        service_name=service_name,
        login=login,
        encrypted_password=encrypted_password,
    )
    with Session() as session:
        session.add(credential)
        session.commit()


def get_credentials_by_service(service_name: str) -> list[Credential]:
    """Busca as credenciais de um servico. Lista vazia se nao houver nenhuma.

    Devolve lista porque service_name nao tem constraint de unicidade: o
    mesmo servico pode ter mais de um login.
    """
    with Session() as session:
        query = (
            select(Credential)
            .where(Credential.service_name == service_name)
            .order_by(Credential.id)
        )
        return list(session.execute(query).scalars().all())


def get_all_credentials() -> list[Credential]:
    """Devolve todas as credenciais do vault, sem filtro."""
    with Session() as session:
        query = select(Credential).order_by(Credential.service_name, Credential.id)
        return list(session.execute(query).scalars().all())


def delete_credential(credential_id: int) -> bool:
    """Apaga a credencial de id informado. Irreversivel.

    Devolve True se apagou, False se nao existe linha com esse id.
    """
    with Session() as session:
        credential = session.get(Credential, credential_id)
        if credential is None:
            return False

        session.delete(credential)
        session.commit()
        return True


def update_credential_password(credential_id: int, encrypted_password: bytes) -> bool:
    """Substitui a senha de uma credencial. A senha ja deve chegar cifrada.

    Devolve True se atualizou, False se nao existe linha com esse id.
    O updated_at do modelo se atualiza sozinho no commit (onupdate).
    """
    with Session() as session:
        credential = session.get(Credential, credential_id)
        if credential is None:
            return False
        credential.encrypted_password = encrypted_password
        session.commit()
        return True


def get_credential_by_id(credential_id: int) -> Credential | None:
    """Busca uma credencial pela chave primaria. None se nao existir.

    Usada pela CLI para exibir servico e login antes de apagar ou alterar,
    para o usuario conferir que digitou o id certo.
    """
    with Session() as session:
        credential = session.get(Credential, credential_id)
        return credential


def search_credentials_by_service(term: str) -> list[Credential]:
    """Busca credenciais cujo service_name contenha o termo, sem diferenciar caixa.

    Usa ILIKE do Postgres com o termo cercado de '%' (coringa de qualquer
    sequencia de caracteres). Se o termo tiver '%' ou '_', eles funcionam
    como coringa tambem, sem escape (aceito de proposito, YAGNI).
    """
    with Session() as session:
        query = (
            select(Credential)
            .where(Credential.service_name.ilike(f"%{term}%"))
            .order_by(Credential.service_name, Credential.id)
        )
        return list(session.execute(query).scalars().all())
