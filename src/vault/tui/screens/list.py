from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Input

from vault.db.credentials import get_all_credentials, search_credentials_by_service


class ListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DataTable(id="ListaServicos")
        yield Input(placeholder="Buscar por serviço...", id="busca")

    def on_mount(self) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.add_columns("ID", "Serviço", "Login")
        for credential in get_all_credentials():
            tabela.add_row(credential.id, credential.service_name, credential.login)

    def on_input_changed(self, event: Input.Changed) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.clear()
        if event.value == "":
            for credential in get_all_credentials():
                tabela.add_row(credential.id, credential.service_name, credential.login)
        else:
            for credential in search_credentials_by_service(event.value):
                tabela.add_row(credential.id, credential.service_name, credential.login)
