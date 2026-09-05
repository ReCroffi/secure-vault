from vault.db.credentials import (
    delete_credential,
    get_all_credentials,
    get_credential_by_id,
    get_credentials_by_service,
    save_credential,
    search_credentials_by_service,
    update_credential_password,
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


def test_get_all_credentials_vazio():
    assert get_all_credentials() == []


def test_get_all_credentials_retorna_todas():
    service_name_b = "teste_b"
    login_user_name_b = "teste_b@teste.b.com"
    encrypted_password_b = b"senha_teste_b"
    service_name_a = "teste_a"
    login_user_name_a = "teste_a@teste.a.com"
    encrypted_password_a = b"senha_teste_a"
    save_credential(service_name_b, login_user_name_b, encrypted_password_b)
    save_credential(service_name_a, login_user_name_a, encrypted_password_a)
    credentials = get_all_credentials()
    assert len(credentials) == 2 and credentials[0].service_name == service_name_a


def test_delete_credential_apaga():
    service_name = "teste"
    login_user_name = "teste@teste.com"
    encrypted_password = b"senha_teste"
    save_credential(service_name, login_user_name, encrypted_password)
    credentials = get_credentials_by_service(service_name)
    credential_id = credentials[0].id
    deleted = delete_credential(credential_id)
    assert deleted is True
    assert get_credential_by_id(credential_id) is None


def test_delete_credential_nao_encontra():
    deleted = delete_credential(999)
    assert deleted is False


def test_update_credential_password_atualiza():
    service_name = "teste"
    login_user_name = "teste@teste.com"
    encrypted_password = b"senha_teste"
    save_credential(service_name, login_user_name, encrypted_password)
    credentials = get_credentials_by_service(service_name)
    credential_id = credentials[0].id
    new_encrypted_password = b"nova_senha"
    updated = update_credential_password(credential_id, new_encrypted_password)
    assert updated is True
    check_updated_pass = get_credential_by_id(credential_id)
    assert check_updated_pass.encrypted_password == new_encrypted_password


def test_update_credential_password_nao_encontra():
    assert update_credential_password(999, b"senha_qualquer") is False


def test_search_credentials_by_service_casa_meio_do_nome():
    service_name_1 = "teste1"
    login_user_name_1 = "teste1@teste.com"
    encrypted_password_1 = b"senha_teste1"
    service_name_2 = "teste2"
    login_user_name_2 = "teste2@teste.com"
    encrypted_password_2 = b"senha_teste2"
    service_name_3 = "conta-gmail-trabalho"
    login_user_name_3 = "teste@gmail.com"
    encrypted_password_3 = b"senha_teste3"
    save_credential(service_name_1, login_user_name_1, encrypted_password_1)
    save_credential(service_name_2, login_user_name_2, encrypted_password_2)
    save_credential(service_name_3, login_user_name_3, encrypted_password_3)
    credential = search_credentials_by_service("gmail")
    assert len(credential) == 1 and credential[0].service_name == service_name_3


def test_search_credentials_by_service_ignora_maiuscula_minuscula():
    service_name_1 = "teste1"
    login_user_name_1 = "teste1@teste.com"
    encrypted_password_1 = b"senha_teste1"
    service_name_2 = "teste2"
    login_user_name_2 = "teste2@teste.com"
    encrypted_password_2 = b"senha_teste2"
    service_name_3 = "cOnTa-gMAIl-traBaLhO"
    login_user_name_3 = "teste@gmail.com"
    encrypted_password_3 = b"senha_teste3"
    save_credential(service_name_1, login_user_name_1, encrypted_password_1)
    save_credential(service_name_2, login_user_name_2, encrypted_password_2)
    save_credential(service_name_3, login_user_name_3, encrypted_password_3)
    credential = search_credentials_by_service("gmail")
    assert len(credential) == 1 and credential[0].service_name == service_name_3


def test_search_credentials_by_service_sem_match():
    service_name_1 = "teste1"
    login_user_name_1 = "teste1@teste.com"
    encrypted_password_1 = b"senha_teste1"
    service_name_2 = "teste2"
    login_user_name_2 = "teste2@teste.com"
    encrypted_password_2 = b"senha_teste2"
    service_name_3 = "cOnTa-gMAIl-traBaLhO"
    login_user_name_3 = "teste@gmail.com"
    encrypted_password_3 = b"senha_teste3"
    save_credential(service_name_1, login_user_name_1, encrypted_password_1)
    save_credential(service_name_2, login_user_name_2, encrypted_password_2)
    save_credential(service_name_3, login_user_name_3, encrypted_password_3)
    credential = search_credentials_by_service("netflix")
    assert credential == []
