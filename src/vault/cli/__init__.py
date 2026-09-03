import typer

from vault.core.crypto import decrypt_password, encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import (
    get_all_credentials,
    get_credentials_by_service,
    save_credential,
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
    """Guarda uma nova credencial, cifrando a senha do servico."""
    password = typer.prompt(
        "Senha do serviço", hide_input=True, confirmation_prompt=True
    )
    key = _get_key()
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
        typer.echo(f"Service: {service}\nLogin: {username}")
