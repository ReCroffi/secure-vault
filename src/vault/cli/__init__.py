import typer

from vault.core.crypto import decrypt_password, encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import get_credentials_by_service, save_credential

app = typer.Typer()


@app.command()
def init():
    password = typer.prompt("Senha mestra", hide_input=True, confirmation_prompt=True)

    try:
        create_vault(password=password)
        typer.echo("Vault criado com sucesso")
    except ValueError as e:
        typer.echo(e)


def main() -> None:

    app()


def _get_key() -> bytes:
    password = typer.prompt("Senha mestra", hide_input=True)
    try:
        return login(password)

    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@app.command()
def add(service_name: str, username: str):
    password = typer.prompt(
        "Senha do serviço", hide_input=True, confirmation_prompt=True
    )
    key = _get_key()
    encrypted_password = encrypt_password(password, key)
    save_credential(service_name, username, encrypted_password)
    typer.echo("Adicionado com sucesso")


@app.command()
def get(service_name: str):
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
