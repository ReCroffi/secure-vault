import typer

from vault.core.crypto import decrypt_password, encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import (
    delete_credential,
    get_all_credentials,
    get_credential_by_id,
    get_credentials_by_service,
    save_credential,
    update_credential_password,
)

app = typer.Typer()


@app.command()
def init():
    """Cria o vault, definindo a senha mestra."""
    password = typer.prompt("Senha mestra", hide_input=True, confirmation_prompt=True)

    try:
        create_vault(password=password)
        typer.echo("Vault criado com sucesso")
    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(code=1)


def main() -> None:
    """Ponto de entrada do executavel `secure-vault` (ver [project.scripts])."""
    app()


def _get_key() -> bytes:
    """Pede a senha mestra e devolve a chave de cifragem derivada dela.

    Encerra o programa com codigo 1 se a senha estiver errada.
    """
    password = typer.prompt("Senha mestra", hide_input=True)
    try:
        return login(password)

    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@app.command()
def add(service_name: str, username: str):
    """Guarda uma nova credencial, cifrando a senha do servico.

    Autentica antes de pedir a senha do servico: se a senha mestra estiver
    errada, o comando encerra sem ter feito o usuario digitar nada.
    """
    key = _get_key()
    password = typer.prompt(
        "Senha do serviço", hide_input=True, confirmation_prompt=True
    )
    encrypted_password = encrypt_password(password, key)
    save_credential(service_name, username, encrypted_password)
    typer.echo("Adicionado com sucesso")


@app.command()
def get(service_name: str):
    """Mostra as credenciais de um servico, com a senha decifrada.

    Consulta o banco antes de pedir a senha mestra, para nao autenticar a
    toa quando o servico nao existe. Sai com codigo 1 nesse caso.
    """
    credentials = get_credentials_by_service(service_name)
    if not credentials:
        typer.echo("Não encontrado")
        raise typer.Exit(code=1)

    key = _get_key()
    for credential in credentials:
        service = credential.service_name
        password = decrypt_password(credential.encrypted_password, key)
        username = credential.login
        typer.echo(f"Service: {service}\nLogin: {username}\nPassword: {password}")


@app.command("list")
def list_credentials():
    """Lista os servicos e logins guardados, sem revelar nenhuma senha.

    Autentica antes de consultar: a propria lista de servicos e informacao
    sensivel. Vault vazio e resposta valida, entao sai com codigo 0.
    """
    _get_key()
    credentials = get_all_credentials()
    if not credentials:
        typer.echo("Vault vazio")
    for credential in credentials:
        service = credential.service_name
        username = credential.login
        credential_id = credential.id
        typer.echo(f"Service: {service}\nLogin: {username}\nID: {credential_id}")


@app.command()
def delete(credential_id: int):
    """Apaga uma credencial pelo id. Irreversivel, pede confirmacao.

    Usa o id (chave primaria) em vez do nome do servico porque o mesmo
    servico pode ter varios logins - apagar por nome levaria todos junto.
    Rode `secure-vault list` para descobrir o id. Sai com codigo 1 se o id
    nao existir.
    """
    _get_key()
    credential = get_credential_by_id(credential_id)
    if credential is None:
        typer.echo("Não encontrado")
        raise typer.Exit(code=1)

    typer.confirm(
        f"Deseja apagar {credential.service_name}: {credential.login}", abort=True
    )
    deleted = delete_credential(credential_id)
    if deleted:
        typer.echo("Apagado com sucesso")
    else:
        typer.echo("Não encontrado")
        raise typer.Exit(code=1)


@app.command("update")
def update_credential(credential_id: int):
    """Troca a senha de uma credencial, identificada pelo id.

    Autentica antes de pedir a senha nova: se a senha mestra estiver
    errada, o comando encerra sem ter feito o usuario digitar nada.
    Rode `secure-vault list` para descobrir o id. Sai com codigo 1 se o id
    nao existir.
    """
    key = _get_key()
    credential = get_credential_by_id(credential_id)
    if credential is None:
        typer.echo("Não encontrado")
        raise typer.Exit(code=1)
    typer.echo(f"Alterando senha de {credential.service_name}: {credential.login}")
    password = typer.prompt(
        "Entre a nova senha", hide_input=True, confirmation_prompt=True
    )
    encrypted_password = encrypt_password(password, key)
    updated = update_credential_password(credential_id, encrypted_password)
    if updated:
        typer.echo("Senha atualizada")
    else:
        typer.echo("Não encontrado")
        raise typer.Exit(code=1)
