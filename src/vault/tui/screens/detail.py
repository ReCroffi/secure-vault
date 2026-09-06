from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from vault.core.crypto import decrypt_password
from vault.db.credentials import delete_credential, get_credential_by_id
from vault.tui.screens.confirm import ConfirmScreen
from vault.tui.screens.edit import EditScreen


class DetailScreen(Screen):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("escape", "voltar", "Voltar"),
        ("d", "apagar", "Apagar"),
        ("e", "editar", "Editar"),
    ]

    def __init__(self, credential_id: int) -> None:
        super().__init__()
        self.credential_id = credential_id

    def compose(self) -> ComposeResult:
        yield Static("Carregando...", id="static")

    def on_mount(self) -> None:
        self._carregar_detalhes()

    def action_voltar(self) -> None:
        self.app.pop_screen()

    def action_apagar(self) -> None:
        credential = get_credential_by_id(self.credential_id)
        self.app.push_screen(
            ConfirmScreen(
                f"Tem certeza que deseja apagar a credencial para '{credential.service_name}'?"
            ),
            self.on_confirm_apagar,
        )

    def on_confirm_apagar(self, confirmed: bool) -> None:
        if confirmed:
            delete_credential(self.credential_id)

    def action_editar(self) -> None:
        self.app.push_screen(EditScreen(self.credential_id))

    def _carregar_detalhes(self) -> None:
        credential = get_credential_by_id(self.credential_id)
        if credential is None:
            self.app.pop_screen()
            return
        decrypted_password = decrypt_password(
            credential.encrypted_password, self.app.key
        )
        self.query_one("#static", Static).update(
            f"Serviço: {credential.service_name}\nLogin: {credential.login}\nSenha: {decrypted_password}"
        )

    def on_screen_resume(self) -> None:
        self._carregar_detalhes()
