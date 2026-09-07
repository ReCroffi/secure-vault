from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input

from vault.core.crypto import encrypt_password
from vault.core.strength import check_password_strength
from vault.db.credentials import update_credential_password


class EditScreen(Screen):
    senha_fraca_confirmada: bool = False
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [("escape", "cancelar", "Voltar")]

    def __init__(self, credential_id: int) -> None:
        super().__init__()
        self.credential_id = credential_id

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Nova senha", password=True, id="password")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "password":
            password = event.value
            score, warning = check_password_strength(password)
            if score >= 3 or self.senha_fraca_confirmada:
                encrypted_password = encrypt_password(password, self.app.key)
                update_credential_password(self.credential_id, encrypted_password)
                self.app.pop_screen()
            else:
                self.senha_fraca_confirmada = True
                self.notify(
                    f"Senha fraca: {warning}. Pressione Enter novamente para confirmar ou Esc para cancelar.",
                    severity="warning",
                )
                return

    def action_cancelar(self) -> None:
        self.app.pop_screen()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "password":
            self.senha_fraca_confirmada = False
