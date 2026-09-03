import typer

from vault.core.crypto import encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import save_credential

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
