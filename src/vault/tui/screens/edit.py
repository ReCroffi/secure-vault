"""Tela de troca de senha de uma credencial existente.

Mesma logica de confirmacao de senha fraca do AddScreen (ver comentarios
la), so que so pede a senha nova - servico e login nao mudam.
"""

from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input

from vault.core.crypto import encrypt_password
from vault.core.generator import generate_password
from vault.core.strength import check_password_strength
from vault.db.credentials import update_credential_password


class EditScreen(Screen):
    senha_fraca_confirmada: bool = False
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [("escape", "cancelar", "Voltar")]

    def __init__(self, credential_id: int) -> None:
        super().__init__()
        self.credential_id = credential_id  # id da credencial sendo editada

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Nova senha", password=True, id="password")
        yield Button("Gerar senha segura", id="gerador")

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "gerador":
            generated_password = generate_password(16)
            password_input = self.query_one("#password", Input)
            password_input.value = generated_password
            self.app.copy_to_clipboard(generated_password)
            self.notify(
                "Senha gerada e copiada para a área de transferência.",
                severity="info",
            )
            self.senha_fraca_confirmada = False
