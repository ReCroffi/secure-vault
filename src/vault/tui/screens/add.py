"""Tela de cadastro de uma credencial nova (servico + login + senha)."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input

from vault.core.crypto import encrypt_password
from vault.core.generator import generate_password
from vault.core.strength import check_password_strength
from vault.db.credentials import save_credential


class AddScreen(Screen):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("escape", "cancelar", "Voltar"),
    ]
    # Fica True depois que o usuario ja viu o aviso de senha fraca e apertou
    # Enter de novo confirmando "quero usar mesmo assim". Reseta pra False
    # sempre que o campo de senha muda, pra nao "vazar" a confirmacao pra
    # uma senha diferente da que foi avaliada.
    senha_fraca_confirmada: bool = False

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Serviço", id="service_name")
        yield Input(placeholder="Login", id="login")
        yield Input(placeholder="Senha", password=True, id="password")
        yield Button(
            "Gerar senha segura",
            id="gerador",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # So age quando o Enter foi dado no campo de senha (ultimo da tela).
        if event.input.id == "password":
            service_name = self.query_one("#service_name", Input).value
            login = self.query_one("#login", Input).value
            password = event.value
            score, warning = check_password_strength(password)
            if score >= 3 or self.senha_fraca_confirmada:
                encrypted_password = encrypt_password(password, self.app.key)
                save_credential(service_name, login, encrypted_password)
                self.app.pop_screen()
            else:
                # Primeira vez com senha fraca: nao salva ainda, so avisa e
                # arma a flag - o proximo Enter (sem mudar a senha) confirma.
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
