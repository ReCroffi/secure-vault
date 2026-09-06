from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Input

from vault.db.credentials import get_all_credentials, search_credentials_by_service
from vault.tui.screens.detail import DetailScreen


class ListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DataTable(id="ListaServicos", cursor_type="row")
        yield Input(placeholder="Buscar por serviço...", id="busca")

    def on_mount(self) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.add_columns("ID", "Serviço", "Login")
        for credential in get_all_credentials():
            tabela.add_row(
                credential.id,
                credential.service_name,
                credential.login,
                key=str(credential.id),
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.clear()
        if event.value == "":
            for credential in get_all_credentials():
                tabela.add_row(
                    credential.id,
                    credential.service_name,
                    credential.login,
                    key=str(credential.id),
                )
        else:
            for credential in search_credentials_by_service(event.value):
                tabela.add_row(
                    credential.id,
                    credential.service_name,
                    credential.login,
                    key=str(credential.id),
                )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        key = int(event.row_key.value)
        self.app.push_screen(DetailScreen(key))
