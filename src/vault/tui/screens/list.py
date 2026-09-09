"""Tela principal: tabela com todas as credenciais + busca por servico.

E a tela pra onde tudo volta (login -> aqui; aqui -> add/detail -> aqui de
novo), por isso ela precisa recarregar a tabela toda vez que reaparece
(`on_screen_resume`), nao so no primeiro mount.
"""

from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Input

from vault.db.credentials import get_all_credentials, search_credentials_by_service
from vault.tui.screens.add import AddScreen
from vault.tui.screens.detail import DetailScreen


class ListScreen(Screen):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("a", "adicionar", "Adicionar"),
    ]

    def compose(self) -> ComposeResult:
        yield DataTable(id="ListaServicos", cursor_type="row")
        yield Input(placeholder="Buscar por serviço...", id="busca")

    def _popular_tabela(self, tabela: DataTable, search_term: str = "") -> None:
        """Limpa e repopula a tabela. Sem termo de busca, lista tudo; com
        termo, filtra pelo nome do servico (ver `search_credentials_by_service`).
        `key=str(credential.id)` em cada linha e o que permite recuperar o id
        selecionado em `on_data_table_row_selected`."""
        tabela.clear()
        if search_term == "":
            credentials = get_all_credentials()
            for credential in sorted(credentials, key=lambda c: c.id):
                tabela.add_row(
                    credential.id,
                    credential.service_name,
                    credential.login,
                    key=str(credential.id),
                )

        else:
            credentials = search_credentials_by_service(search_term)
            for credential in sorted(credentials, key=lambda c: c.id):
                tabela.add_row(
                    credential.id,
                    credential.service_name,
                    credential.login,
                    key=str(credential.id),
                )

    def on_mount(self) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        tabela.add_columns("ID", "Serviço", "Login")
        self._popular_tabela(tabela)

    def on_input_changed(self, event: Input.Changed) -> None:
        tabela = self.query_one("#ListaServicos", DataTable)
        self._popular_tabela(tabela, event.value)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        key = int(event.row_key.value)
        self.app.push_screen(DetailScreen(key))

    def action_adicionar(self) -> None:
        self.app.push_screen(AddScreen())

    def on_screen_resume(self) -> None:
        # Disparado quando essa tela volta ao topo da pilha (ex.: usuario
        # apertou Esc no AddScreen ou voltou do DetailScreen). Recarrega a
        # tabela pra refletir credenciais criadas/apagadas/editadas nesse meio-tempo.
        tabela = self.query_one("#ListaServicos", DataTable)
        self._popular_tabela(tabela)
