import typer

from vault.core.master_password import create_vault, login

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
