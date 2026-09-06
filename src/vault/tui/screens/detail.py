from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from vault.core.crypto import decrypt_password
from vault.db.credentials import delete_credential, get_credential_by_id
from vault.tui.screens.confirm import ConfirmScreen


class DetailScreen(Screen):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("escape", "voltar", "Voltar"),
        ("d", "apagar", "Apagar"),
    ]

    def __init__(self, credential_id: int) -> None:
        super().__init__()
        self.credential_id = credential_id

    def compose(self) -> ComposeResult:
        yield Static("Carregando...", id="static")

    def on_mount(self) -> None:
        credential = get_credential_by_id(self.credential_id)
        decrypted_password = decrypt_password(
            credential.encrypted_password, self.app.key
        )
        self.query_one("#static", Static).update(
            f"Serviço: {credential.service_name}\nLogin: {credential.login}\nSenha: {decrypted_password}"
        )

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
            self.app.pop_screen()
