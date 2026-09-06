from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input

from vault.core.crypto import encrypt_password
from vault.db.credentials import save_credential


class AddScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Serviço", id="service_name")
        yield Input(placeholder="Login", id="login")
        yield Input(placeholder="Senha", password=True, id="password")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "password":
            service_name = self.query_one("#service_name", Input).value
            login = self.query_one("#login", Input).value
            password = event.value
            encrypted_password = encrypt_password(password, self.app.key)
            save_credential(service_name, login, encrypted_password)            
            self.app.pop_screen()