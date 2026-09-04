from vault.db.credentials import (
    get_credential_by_id,
    get_credentials_by_service,
    save_credential,
)


def test_save_credential_persiste():
    service_name = "teste"
    login_user_name = "teste@teste.com"
    encrypted_password = b"senha_teste"
    save_credential(service_name, login_user_name, encrypted_password)
    credentials = get_credentials_by_service(service_name)
    service = credentials[0].service_name
    password = credentials[0].encrypted_password
    user_name = credentials[0].login

    assert (
        len(credentials) == 1
        and service_name == service
        and encrypted_password == password
        and login_user_name == user_name
    )


def test_get_credential_by_id_encontra():
    service_name = "teste"
    login_user_name = "teste@teste.com"
    encrypted_password = b"senha_teste"
    save_credential(service_name, login_user_name, encrypted_password)
    credentials = get_credentials_by_service(service_name)
    credential_id = credentials[0].id
    consulta_id = get_credential_by_id(credential_id)

    assert (
        consulta_id is not None
        and service_name == consulta_id.service_name
        and login_user_name == consulta_id.login
    )


def test_get_credential_by_id_nao_encontra():
    consulta_id = get_credential_by_id(999)
    assert consulta_id is None
