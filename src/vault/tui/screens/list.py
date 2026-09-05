from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable

from vault.db.credentials import get_all_credentials


class ListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DataTable(id="ListaServicos")

    def on_mount(self) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.add_columns("ID", "Serviço", "Login")
        for credential in get_all_credentials():
            tabela.add_row(credential.id, credential.service_name, credential.login)
